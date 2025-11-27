import cProfile
import pstats
import time
import psutil
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from src.config.db import SessionLocal
from src.models.profiling import ProfilingLog


class ProfilingMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, enabled: bool = False):
        super().__init__(app)
        self.enabled = enabled
        self.process = psutil.Process()
    
    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)
        
        cpu_before = self.process.cpu_percent()
        mem_before = self.process.memory_info().rss / 1024 / 1024
        
        profiler = cProfile.Profile()
        profiler.enable()
        
        start_time = time.perf_counter()
        response = await call_next(request)
        total_time = (time.perf_counter() - start_time) * 1000
        
        profiler.disable()
        
        cpu_after = self.process.cpu_percent()
        mem_after = self.process.memory_info().rss / 1024 / 1024
        
        stats = pstats.Stats(profiler)
        
        top_functions = self._extract_top_functions(stats, limit=10)
        timings = self._extract_specific_timings(stats)
        
        ncalls_total, ncalls_pandas, ncalls_db = self._count_calls_by_category(stats)
        
        self._save_to_database(
            endpoint=request.url.path,
            method=request.method,
            total_time_ms=total_time,
            top_functions=top_functions,
            timings=timings,
            ncalls_total=ncalls_total,
            ncalls_pandas=ncalls_pandas,
            ncalls_database=ncalls_db,
            cpu_percent=(cpu_after - cpu_before),
            memory_mb=(mem_after - mem_before),
        )
        
        return response
    
    def _extract_top_functions(self, stats: pstats.Stats, limit: int = 10) -> list:
        stats.sort_stats(pstats.SortKey.CUMULATIVE)
        
        top_funcs = []
        for func, data in list(stats.stats.items())[:limit]:
            cc, nc, tt, ct, callers = data
            filename, line, func_name = func

            top_funcs.append({
                "name": func_name,
                "file": filename.split("/")[-1],
                "line": line,
                "time_ms": ct * 1000,
                "calls": nc,
            })
        
        return top_funcs
    
    def _extract_specific_timings(self, stats: pstats.Stats) -> dict:
        timings = {
            "preprocessing": 0.0,
            "inference": 0.0,
            "database": 0.0,
            "serialization": 0.0,
        }
        
        for func, data in stats.stats.items():
            cc, nc, tt, ct, callers = data
            filename, line, func_name = func
            time_ms = ct * 1000
            
            func_name_lower = func_name.lower()
            file_name_lower = filename.lower()
            
            # Preprocessing
            if "compute_features" in func_name_lower or "features.py" in file_name_lower:
                timings["preprocessing"] += time_ms
            
            # Inference
            elif "predict_proba" in func_name_lower:
                timings["inference"] += time_ms
            
            # Database
            elif "psycopg" in file_name_lower or "sqlalchemy" in file_name_lower:
                if any(kw in func_name_lower for kw in ["wait", "execute", "flush", "commit"]):
                    timings["database"] += time_ms
            
            # Serialization
            elif any(kw in func_name_lower for kw in ["json", "dumps", "serialize"]):
                timings["serialization"] += time_ms
        
        return timings
    
    def _count_calls_by_category(self, stats: pstats.Stats) -> tuple[int, int, int]:
        ncalls_total = 0
        ncalls_pandas = 0
        ncalls_db = 0
        
        for func, data in stats.stats.items():
            cc, nc, tt, ct, callers = data
            filename, line, func_name = func

            ncalls_total += nc
            
            if "pandas" in filename:
                ncalls_pandas += nc
            elif "sqlalchemy" in filename or "psycopg" in filename:
                ncalls_db += nc
        
        return ncalls_total, ncalls_pandas, ncalls_db
    
    def _save_to_database(
        self,
        endpoint: str,
        method: str,
        total_time_ms: float,
        top_functions: list,
        timings: dict,
        ncalls_total: int,
        ncalls_pandas: int,
        ncalls_database: int,
        cpu_percent: float,
        memory_mb: float,
    ):
        db: Session = SessionLocal()
        try:
            time_preprocessing = timings.get("preprocessing") or None
            time_inference = timings.get("inference") or None
            time_database = timings.get("database") or None
            time_serialization = timings.get("serialization") or None

            log = ProfilingLog(
                endpoint=endpoint,
                method=method,
                total_time_ms=total_time_ms,
                time_preprocessing_ms=time_preprocessing,
                time_inference_ms=time_inference,
                time_database_ms=time_database,
                time_serialization_ms=time_serialization,
                top_functions=top_functions,
                ncalls_total=ncalls_total,
                ncalls_pandas=ncalls_pandas,
                ncalls_database=ncalls_database,
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
            )
            
            db.add(log)
            db.commit()
                        
        except Exception:
            import traceback
            traceback.print_exc()
            db.rollback()
        finally:
            db.close()

from concurrent.futures import ThreadPoolExecutor, wait

def run_parallel(items):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for item in items:
            task = item[0]
            args = item[1] if len(item) > 1 else []
            kwargs = item[2] if len(item) > 2 else {}
            future = executor.submit(task, *args, **kwargs)
            futures.append(future)
    done_futures, _ = wait(futures)
    return [future.result() for future in done_futures]

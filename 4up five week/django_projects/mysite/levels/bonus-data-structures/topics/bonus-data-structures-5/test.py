q = Queue()
q.enqueue(1)
q.enqueue(2)

peek_result = q.peek()
dequeue_result1 = q.dequeue()
dequeue_result2 = q.dequeue()
empty_result = q.is_empty()

jobs = ["報告.pdf", "海報.pdf", "課表.pdf"]
simulate_print_jobs_result = simulate_print_jobs(jobs)
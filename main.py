import heapq
from collections import deque
import copy

#Process class for use by the algorithms
class Process:
    def __init__(self, pid, arrival_time, burst_time):
        #process ID
        self.pid = pid
        #When the process shows up
        self.arrival_time = arrival_time
        #How long it takes the CPU to complete the task
        self.burst_time = burst_time

        self.remaining_time = burst_time
        self.start_time = -1
        self.completion_time = -1

        self.waiting_time = -1
        self.turnaround_time = -1

    # For comparing processes based on remaining time
    def __lt__(self, other):
        if self.remaining_time != other.remaining_time:
            return self.remaining_time < other.remaining_time
        if self.arrival_time != other.arrival_time:
            return self.arrival_time < other.arrival_time
        return self.pid < other.pid
    #prints process information
    def __repr__(self):
        return (f"Process(pid={self.pid}, arrival={self.arrival_time}, "
                f"burst={self.burst_time}, remaining={self.remaining_time})")


# 1. Shortest Remaining Time First (SRTF) Implementation
def srtf_scheduler(processes_input):
    # Use a deep copy to avoid modifying the original list objects
    processes = copy.deepcopy(processes_input)
    processes.sort(key=lambda p: p.arrival_time)
    num_processes = len(processes)
    completed_processes_list = []
    scheduled_order = []
    ready_queue = []
    current_time = 0
    processes_completed = 0
    process_idx = 0
    current_process = None
    last_event_time = 0
    is_cpu_idle = True

    while processes_completed < num_processes:
        # Add newly arrived processes to the ready queue
        while process_idx < num_processes and processes[process_idx].arrival_time <= current_time:
            newly_arrived_process = processes[process_idx]
            heapq.heappush(ready_queue, newly_arrived_process)
            print(f"Time {current_time}: Process {newly_arrived_process.pid} arrived, added to ready queue.")
            process_idx += 1
            #when a process arrives it checks if that process has less remaining time then the current process
            #if it does then it interupts the current process and starts the other one
            if current_process is not None and newly_arrived_process.remaining_time < current_process.remaining_time:
                 print(f"Time {current_time}: Newly arrived Process {newly_arrived_process.pid} (RT: {newly_arrived_process.remaining_time}) preempts running Process {current_process.pid} (RT: {current_process.remaining_time}).")
                 if current_time > last_event_time:
                     scheduled_order.append((current_process.pid, last_event_time, current_time))

                 heapq.heappush(ready_queue, current_process)
                 current_process = None
                 is_cpu_idle = True

        #if the cpu is not doing anything and there are processes still waiting then pick a process
        if is_cpu_idle and ready_queue:
            current_process = heapq.heappop(ready_queue)
            is_cpu_idle = False
            if current_process.start_time == -1:
                current_process.start_time = current_time

            print(f"Time {current_time}: Process {current_process.pid} starts/resumes execution (Remaining: {current_process.remaining_time:.2f}).")
            last_event_time = current_time

        #even if the cpu is doing something, still check to see if it should switch processes
        elif not is_cpu_idle and ready_queue:
             if current_process is not None and ready_queue[0].remaining_time < current_process.remaining_time:
                print(f"Time {current_time}: Process {ready_queue[0].pid} in queue (RT: {ready_queue[0].remaining_time:.2f}) preempts running Process {current_process.pid} (RT: {current_process.remaining_time:.2f}).")
                if current_time > last_event_time:
                    scheduled_order.append((current_process.pid, last_event_time, current_time))
                heapq.heappush(ready_queue, current_process)
                current_process = heapq.heappop(ready_queue)
                if current_process.start_time == -1: # First time running
                     current_process.start_time = current_time

                print(f"Time {current_time}: Process {current_process.pid} starts execution.")
                last_event_time = current_time


        if not is_cpu_idle and current_process is not None:
             # Determine time until next event
            time_to_next_arrival = float('inf')
            if process_idx < num_processes:
                time_to_next_arrival = processes[process_idx].arrival_time - current_time

            time_to_completion = current_process.remaining_time


            time_to_potential_preemption = float('inf')
            if ready_queue:
                 if current_process.remaining_time > ready_queue[0].remaining_time:
                     time_diff = current_process.remaining_time - ready_queue[0].remaining_time
                     time_to_potential_preemption = time_diff # Check exactly when they become equal, preemption happens next moment

            time_step = max(1, min(time_to_next_arrival if time_to_next_arrival > 0 else float('inf'),
                                   time_to_completion,
                                   time_to_potential_preemption if time_to_potential_preemption > 0 else float('inf')
                                   ))


            # Execute for time_step
            exec_time = min(time_step, current_process.remaining_time) # Cannot execute more than remaining time
            current_process.remaining_time -= exec_time
            current_time += exec_time
            print(f"Time {current_time}: Process {current_process.pid} executed for {exec_time:.2f}. Remaining time: {current_process.remaining_time:.2f}")

            # Check for completion
            if current_process.remaining_time <= 0.00001:
                current_process.completion_time = current_time
                current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
                current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
                completed_processes_list.append(current_process)
                processes_completed += 1
                print(f"Time {current_time}: Process {current_process.pid} completed.")
                scheduled_order.append((current_process.pid, last_event_time, current_time))
                current_process = None
                is_cpu_idle = True


        elif is_cpu_idle and not ready_queue and process_idx < num_processes:
            idle_start = current_time
            current_time = processes[process_idx].arrival_time
            print(f"Time {idle_start:.2f}-{current_time:.2f}: CPU Idle.")
            last_event_time = current_time

        # If CPU isn't doing anything, queue is empty, and all processes have arrived but not all completed
        elif is_cpu_idle and not ready_queue and process_idx == num_processes and processes_completed < num_processes:
             print(f"Time {current_time}: CPU Idle, waiting. Should not happen for long.")
             # To prevent potential infinite loop if something is wrong:
             current_time += 1


        #all processes accounted for and all completed
        elif processes_completed == num_processes and process_idx == num_processes:
             break


    # Sort completed list by PID for consistent reporting
    completed_processes_list.sort(key=lambda p: p.pid)
    return scheduled_order, completed_processes_list


# 2. Multi Level Feedback Queue (MLFQ) Implementation
def mlfq_scheduler(processes_input, time_quantums=[5, 10, float('inf')], num_queues=3):
    # Use deep copies to keep original process data intact for metrics
    processes_original = {p.pid: p for p in processes_input}
    process_copies = copy.deepcopy(processes_input)
    process_copies.sort(key=lambda p: p.arrival_time) # Sort by arrival time

    num_processes = len(process_copies)
    completed_processes_list = [] # Store original objects with updated metrics
    scheduled_order = []
    # Queues for each level, holding Process objects (copies)
    queues = [deque() for _ in range(num_queues)]
    # Keep track of which queue each process (by pid) is currently in
    process_queue_level = {p.pid: -1 for p in process_copies}

    current_time = 0
    processes_completed = 0
    process_idx = 0 # Index for the sorted list of arriving processes
    current_process = None # The process currently holding the CPU
    current_queue_level = -1 # The queue the current_process came from
    time_slice_left = 0 # Time left in the current quantum for the running process
    last_event_time = 0 # Start time of the current execution block
    is_cpu_idle = True


    print("MLFQ Run Start")
    print(f"Queues: {num_queues}, Time Quantums: {time_quantums}")

    while processes_completed < num_processes:
        #First thing that is checked on every loop is the new processes
        newly_arrived_pids = []
        while process_idx < num_processes and process_copies[process_idx].arrival_time <= current_time:
            #new processes start at the top of the priority queue
            arriving_process = process_copies[process_idx]
            print(f"Time {current_time:.2f}: Process {arriving_process.pid} arrived, added to Q0.")
            queues[0].append(arriving_process)
            process_queue_level[arriving_process.pid] = 0
            newly_arrived_pids.append(arriving_process.pid)
            process_idx += 1

        #Preemption Check on Arrival
        # If a high-priority process arrived and CPU is running a lower-priority process is running, then stop the
        #current process and work on the higher priority process.
        if newly_arrived_pids and not is_cpu_idle and current_process is not None and current_queue_level > 0:
            # Check if any new arrival is in Q0 (highest priority)
             needs_preemption = any(process_queue_level[pid] == 0 for pid in newly_arrived_pids)
             if needs_preemption:
                print(f"Time {current_time:.2f}: Arrival in Q0 preempts Process {current_process.pid} (running from Q{current_queue_level}).")
                # Record execution segment of the preempted process
                if current_time > last_event_time:
                     scheduled_order.append((current_process.pid, last_event_time, current_time))
                # Put the preempted process back to the front of its queue (as it didn't finish its slice)
                queues[current_queue_level].appendleft(current_process)
                current_process = None # CPU becomes available
                is_cpu_idle = True
                current_queue_level = -1


        #Choose a process if the queue is empty
        if is_cpu_idle:
            selected = False
            #check queues from highest to lowest
            for level in range(num_queues):
                if queues[level]:
                    current_process = queues[level].popleft()
                    current_queue_level = level
                    process_queue_level[current_process.pid] = level # Update tracker
                    time_slice_left = time_quantums[level]
                    is_cpu_idle = False

                    # Record start time for the original process
                    original_process = processes_original[current_process.pid]
                    if original_process.start_time == -1:
                        original_process.start_time = current_time


                    print(f"Time {current_time:.2f}: Process {current_process.pid} selected from Q{current_queue_level}"
                          f" to run (Quantum: {time_slice_left}, Remaining: {current_process.remaining_time:.2f}).")
                    last_event_time = current_time
                    selected = True
                    break # Stop searching for processes once one is found

            # If there was no current process found in all the queues...
            if not selected:
                 #And there are processes that are still to be done...
                 if process_idx < num_processes:
                     #THEN skip forward the time to the next arrival time
                     idle_start = current_time
                     current_time = process_copies[process_idx].arrival_time
                     print(f"Time {idle_start:.2f}-{current_time:.2f}: CPU Idle.")
                     last_event_time = current_time
                     continue # Re-evaluate at the new time
                 # If all arrived but not all completed (means queues empty - should only happen if finished)
                 elif processes_completed < num_processes:
                      print(f"Time {current_time:.2f}: CPU Idle, but processes remain? Ending simulation (check logic).")
                      break # Avoid infinite loop
                 else: # All processes arrived and completed
                      break


        #Runs if the cpu has a task to work on
        if not is_cpu_idle and current_process is not None:
            time_to_next_arrival = float('inf')
            if process_idx < num_processes:
                time_to_next_arrival = process_copies[process_idx].arrival_time - current_time

            run_for = min(time_slice_left, current_process.remaining_time)

            time_step = max(1.0, min(run_for, time_to_next_arrival if time_to_next_arrival > 0 else float('inf'))) # Ensure time advances
            exec_time = min(time_step, run_for) # Actual execution time in this step

            current_process.remaining_time -= exec_time
            time_slice_left -= exec_time
            current_time += exec_time
            print(f"Time {current_time:.2f}: Process {current_process.pid} (Q{current_queue_level}) ran for {exec_time:.2f}. Remaining: {current_process.remaining_time:.2f}. Slice left: {time_slice_left:.2f}")

            # Check for completion
            if current_process.remaining_time <= 0.00001:
                original_process = processes_original[current_process.pid]
                original_process.completion_time = current_time
                original_process.turnaround_time = original_process.completion_time - original_process.arrival_time
                original_process.waiting_time = original_process.turnaround_time - original_process.burst_time
                # Add the original process with final metrics to the completed list
                completed_processes_list.append(original_process)

                processes_completed += 1
                print(f"Time {current_time:.2f}: Process {current_process.pid} completed.")
                scheduled_order.append((current_process.pid, last_event_time, current_time))
                process_queue_level[current_process.pid] = -1 # Mark as completed
                current_process = None
                is_cpu_idle = True
                current_queue_level = -1

            # Checks if the processed used all of its allotted time and if it has then move to the next process.
            elif time_slice_left <= 0.00001:
                next_queue_level = min(current_queue_level + 1, num_queues - 1)
                print(f"Time {current_time:.2f}: Process {current_process.pid} quantum expired in Q{current_queue_level}."
                      f" Moving to Q{next_queue_level}.")
                scheduled_order.append((current_process.pid, last_event_time, current_time))
                queues[next_queue_level].append(current_process) # Add to the end of the next queue
                process_queue_level[current_process.pid] = next_queue_level
                current_process = None
                is_cpu_idle = True
                current_queue_level = -1

    print("MLFQ Run End")

    # Sort completed list by PID for consistent reporting
    completed_processes_list.sort(key=lambda p: p.pid)
    return scheduled_order, completed_processes_list


# Helper function to calculate and print average metrics
def calculate_and_print_metrics(completed_processes, algorithm_name, start_time=0):
    if not completed_processes:
        print(f"\n--- {algorithm_name} Performance Metrics ---")
        print("No processes completed.")
        return {}

    num_processes = len(completed_processes)
    total_waiting_time = sum(p.waiting_time for p in completed_processes)
    total_turnaround_time = sum(p.turnaround_time for p in completed_processes)


    avg_waiting_time = total_waiting_time / num_processes
    avg_turnaround_time = total_turnaround_time / num_processes


    # For CPU Util and Throughput
    last_completion_time = max(p.completion_time for p in completed_processes) if completed_processes else start_time
    first_arrival_time = min(p.arrival_time for p in completed_processes) if completed_processes else start_time
    total_simulation_time = last_completion_time - first_arrival_time # More accurate: time from first arrival to last completion
    if total_simulation_time <= 0: total_simulation_time = last_completion_time # Handle case where all arrive at 0

    total_burst_time = sum(p.burst_time for p in completed_processes) # Use original burst times

    cpu_utilization = (total_burst_time / total_simulation_time) * 100 if total_simulation_time > 0 else 0
    throughput = num_processes / total_simulation_time if total_simulation_time > 0 else 0

    print(f"\n{algorithm_name} Performance Measurements")
    print(f"Total Simulation Time: {total_simulation_time:.2f}")
    print(f"Average Waiting Time (AWT): {avg_waiting_time:.2f}")
    print(f"Average Turnaround Time (ATT): {avg_turnaround_time:.2f}")

    print(f"CPU Utilization: {cpu_utilization:.2f}%")
    print(f"Throughput: {throughput:.2f} processes/unit time")

    # Return metrics for potential comparison
    metrics = {
        "AWT": avg_waiting_time,
        "ATT": avg_turnaround_time,
        "CPU_Util": cpu_utilization,
        "Throughput": throughput
    }
    return metrics


#Get User Input
def get_process_input():
    processes = []
    while True:
        try:
            num_proc = int(input("Enter the number of processes: "))
            if num_proc > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

    print("\nEnter process details (Arrival Time and Burst Time):")
    for i in range(num_proc):
        while True:
            try:
                arrival = float(input(f"  Process {i+1} Arrival Time: "))
                burst = float(input(f"  Process {i+1} Burst Time: "))
                if arrival >= 0 and burst > 0:
                    processes.append(Process(pid=i+1, arrival_time=arrival, burst_time=burst))
                    break
                else:
                    print("Arrival time must be >= 0 and Burst time must be > 0.")
            except ValueError:
                print("Invalid input. Please enter numbers.")
    return processes

#Main Execution
if __name__ == "__main__":
    user_processes = get_process_input()

    if not user_processes:
        print("No processes entered. Exiting.")
    else:
        print("\nRunning Schedulers with Provided Processes...")
        print("Initial Processes:")
        for p in user_processes:
            print(f"  PID: {p.pid}, Arrival: {p.arrival_time}, Burst: {p.burst_time}")

        #Run SRTF
        print("\n\nRunning Shortest Remaining Time First(SRTF) Scheduler")
        srtf_schedule, srtf_completed = srtf_scheduler(user_processes)

        print("\nSRTF Execution Order (PID, Start, End):")
        if srtf_schedule:
            for item in srtf_schedule:
                print(f"  PID: {item[0]}, Start: {item[1]:.2f}, End: {item[2]:.2f}")
        else:
            print("  No execution segments.")

        print("\nSRTF Final Process States:")
        if srtf_completed:
             for p in sorted(srtf_completed, key=lambda x: x.pid): # Sort by PID for readability
                  print(f"  PID: {p.pid}, AT: {p.arrival_time:.2f}, BT: {p.burst_time:.2f}, CT: {p.completion_time:.2f}, TAT: {p.turnaround_time:.2f}, WT: {p.waiting_time:.2f}")
        else:
             print("  No processes completed.")
        srtf_metrics = calculate_and_print_metrics(srtf_completed, "SRTF")


        #Run MLFQ
        print("\n\nRunning Multi-Level Feedback Queue(MLFQ) Scheduler")
        # Define MLFQ parameters (can be customized)
        mlfq_quantums = [5, 10, float('inf')] # Example: Q0=5, Q1=10, Q2=FCFS
        mlfq_num_queues = len(mlfq_quantums)
        # Pass the user_processes list again. The function makes its own copy.
        mlfq_schedule, mlfq_completed = mlfq_scheduler(user_processes, time_quantums=mlfq_quantums, num_queues=mlfq_num_queues)

        print("\nMLFQ Execution Order (PID, Start, End):")
        if mlfq_schedule:
            for item in mlfq_schedule:
                print(f"  PID: {item[0]}, Start: {item[1]:.2f}, End: {item[2]:.2f}")
        else:
            print("No execution segments.")

        print("\nMLFQ Final Process States:")
        if mlfq_completed:
             for p in sorted(mlfq_completed, key=lambda x: x.pid): # Sort by PID
                  print(f"  PID: {p.pid}, AT: {p.arrival_time:.2f}, BT: {p.burst_time:.2f}, CT: {p.completion_time:.2f}, TAT: {p.turnaround_time:.2f}, WT: {p.waiting_time:.2f}")
        else:
             print("No processes completed.")

        mlfq_metrics = calculate_and_print_metrics(mlfq_completed, "MLFQ")

        # Metric Results comparison
        print("\n\nMetric Results")
        print(f"{'Metric':<12} | {'SRTF':<10} | {'MLFQ':<10}")
        print("-" * 35)
        print(f"{'AWT':<12} | {srtf_metrics.get('AWT', 'N/A'):<10.2f} | {mlfq_metrics.get('AWT', 'N/A'):<10.2f}")
        print(f"{'ATT':<12} | {srtf_metrics.get('ATT', 'N/A'):<10.2f} | {mlfq_metrics.get('ATT', 'N/A'):<10.2f}")
        print(f"{'CPU Util%':<12} | {srtf_metrics.get('CPU_Util', 'N/A'):<10.2f} | {mlfq_metrics.get('CPU_Util', 'N/A'):<10.2f}")
        print(f"{'Throughput':<12} | {srtf_metrics.get('Throughput', 'N/A'):<10.2f} | {mlfq_metrics.get('Throughput', 'N/A'):<10.2f}")
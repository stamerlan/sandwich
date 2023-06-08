SECTIONS {
    .sandwich_task_ptr : {
        __start_sandwich_task_ptr = .;
        KEEP(*(.sandwich_task_ptr))
        __stop_sandwich_task_ptr = .;
    }
}
INSERT AFTER .text;

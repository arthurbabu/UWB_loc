# 1 "/Applications/SEGGER Embedded Studio for ARM 5.62/samples/SEGGER_THUMB_Startup.s"
# 1 "<built-in>"
# 1 "<command-line>"
# 1 "/Applications/SEGGER Embedded Studio for ARM 5.62/samples/SEGGER_THUMB_Startup.s"
# 62 "/Applications/SEGGER Embedded Studio for ARM 5.62/samples/SEGGER_THUMB_Startup.s"
        .syntax unified
# 88 "/Applications/SEGGER Embedded Studio for ARM 5.62/samples/SEGGER_THUMB_Startup.s"
.macro MARK_FUNC Name
        .global \Name
        .thumb_func
        .code 16
\Name:
.endm




.macro START_FUNC Name
        .section .init.\Name, "ax"
        .global \Name
        .balign 2
        .thumb_func
        .code 16
\Name:
.endm




.macro WEAK_FUNC Name
        .section .init.\Name, "ax", %progbits
        .weak \Name
        .balign 2
        .thumb_func
        .code 16
\Name:
.endm




.macro END_FUNC name
        .size \name,.-\name
.endm







        .extern main
# 162 "/Applications/SEGGER Embedded Studio for ARM 5.62/samples/SEGGER_THUMB_Startup.s"
START_FUNC _start






        ldr R4, =__SEGGER_init_table__
.L_start_RunInit:
        ldr R0, [R4]
        adds R4, R4, #4
        blx R0
        b .L_start_RunInit

MARK_FUNC __SEGGER_init_done
# 186 "/Applications/SEGGER Embedded Studio for ARM 5.62/samples/SEGGER_THUMB_Startup.s"
        bl main

END_FUNC _start




MARK_FUNC exit




        b .
        .size exit,.-exit

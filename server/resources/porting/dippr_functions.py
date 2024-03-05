
__all__ = ["function100", "function101", "function102", "function503", "function509"]
from math import exp, log, sinh, cosh

'''
Function 106, 114, 116 are using receduce temperature.
'''

def arg_arrange(A=0, B=0, C=0, D=0, E=0, F=0, G=0):
    arg = tuple()
    if type(A) in (list, tuple):
        arg += tuple(A)
        if len(arg) > 7:
            arg = arg[:7]
        elif len(arg) < 7:
            arg += (0, ) * (7 - len(arg))
    else:
        arg = (A, B, C, D, E, F, G)
                
    return arg

def function100(A=0, B=0, C=0, D=0, E=0, F=0, G=0):
    arg = arg_arrange(A, B, C, D, E, F, G)

    return lambda T: arg[0] + T * (arg[1] + T * (arg[2] + T * (arg[3] + T * arg[4]))) 

def function101(A=0, B=0, C=0, D=0, E=0, F=0, G=0):
    arg = arg_arrange(A, B, C, D, E, F, G)

    return lambda T: exp (arg[0] + arg[1] / T + arg[2] * log(T) + arg[3] * T **arg[4])

def function102(A=0, B=0, C=0, D=0, E=0, F=0, G=0):
    arg = arg_arrange(A, B, C, D, E, F, G)

    return lambda T: arg[0] * T ** arg[1] / (1 + arg[2] / T + arg[3] / T **2)

def function103(A=0, B=0, C=0, D=0, E=0, F=0, G=0):
    arg = arg_arrange(A, B, C, D, E, F, G)

    return lambda T: arg[0] + arg[1] * exp(- arg[2] / T **arg[3])

def function104(A=0, B=0, C=0, D=0, E=0, F=0, G=0):
    arg = arg_arrange(A, B, C, D, E, F, G)

    return lambda T: arg[0] + (arg[1] + (arg[2] + (arg[3] + arg[4] / T**2) / T**2) / T**2) / T

def function105(A=0, B=0, C=0, D=0, E=0, F=0, G=0):
    arg = arg_arrange(A, B, C, D, E, F, G)

    return lambda T: arg[0] / arg[1] ** (1 + (1 - T / arg[2]) **arg[3])

def function106_Tr(A=0, B=0, C=0, D=0, E=0, F=0, G=0):
    arg = arg_arrange(A, B, C, D, E, F, G)

    return lambda T: arg[0] * (1 - T) ** (arg[1] + T * (arg[2] + T *(arg[3] + T * arg[4])))  

def function107(A=0, B=0, C=0, D=0, E=0, F=0, G=0):
    arg = arg_arrange(A, B, C, D, E, F, G)

    return lambda T: arg[0] + arg[1] * (arg[2] / T / sinh(arg[2] / T)) **2 + arg[3] * (arg[4] / T / cosh(arg[4] / T)) **2

def function114_Tr(A=0, B=0, C=0, D=0, E=0, F=0, G=0):
    arg = arg_arrange(A, B, C, D, E, F, G)

    def f(T):
        t = 1 - T
        fnc = arg[0] ** 2 / t + arg[1] - 2 * arg[0] * arg[2] * t - arg[0] * arg[3] * t **2 - \
            arg[2] **2 * t **3 /3 - arg[2] * arg[3] * t **4 / 2 - arg[3] **2 * t **5 / 5
        return fnc

    return f

def function115(A=0, B=0, C=0, D=0, E=0, F=0, G=0):
    arg = arg_arrange(A, B, C, D, E, F, G)

    return lambda T: exp(arg[0] + arg[1] / T + arg[2] * log(T) + arg[3] * T **2 + arg[4] / T **3)

def function116_Tr(A=0, B=0, C=0, D=0, E=0, F=0, G=0):
    arg = arg_arrange(A, B, C, D, E, F, G)

    def f(T):
        t = 1 - T
        fnc = arg[0] + arg[1] * t **0.35 + arg[2] * t **(2/3) + arg[3] * t + arg[4] * t **(4/3)
        return fnc

    return f

def function127(A=0, B=0, C=0, D=0, E=0, F=0, G=0):
    arg = arg_arrange(A, B, C, D, E, F, G)

    return lambda T: arg[0] + arg[1] * ((arg[2]/T) **2 * exp(arg[2] / T) / (exp(arg[2] / T) - 1)**2) + \
        arg[3] * ((arg[4]/T) **2 * exp(arg[4] / T) / (exp(arg[4] / T) - 1)**2) + \
        arg[5] * ((arg[6]/T) **2 * exp(arg[6] / T) / (exp(arg[6] / T) - 1)**2)

# thermal conduction model for liquid
# As ASPEN method
def function0_TCL(Mw, Tc, Tb):
    def f(T):
        Tbi = Tb / Tc
        Tri = T / Tc
        fnc = 1.1053152 / Mw **2 * (3 + 20 * (1 - Tri) **(2/3)) / (3 + 20 * (1 - Tbi) **(2/3))
        return fnc

    return f

def function503(A=0, B=0, C=0, D=0, E=0, F=0, G=0):
    arg = arg_arrange(A, B, C, D, E, F, G)

    return lambda T: arg[0] + T * (arg[1] + T * (arg[2] + T * arg[3])) 

def function0_VL(A=0, B=0, C=0, D=0, E=0, F=0, G=0):
    arg = arg_arrange(A, B, C, D, E, F, G)

    return lambda T: arg[0] + arg[1] / T + arg[2] * log(T)

# PPDS9
def function301_VL(A=0, B=0, C=0, D=0, E=0, F=0, G=0):
    arg = arg_arrange(A, B, C, D, E, F, G)

    def f(T):
        y = (arg[2] - arg[3]) / (T - arg[3]) - 1
        fnc = arg[4] * exp((arg[0] + arg[1] * y) * y **(1/3))
        return fnc

    return f

# NIST PPDS9 rearrange function
# C5 is using as C1
# then all other Cn shift 1 after
def function509(A=0, B=0, C=0, D=0, E=0, F=0, G=0):
    arg = arg_arrange(A, B, C, D, E, F, G)

    def f(T):
        y = (arg[3] - arg[4]) / (T - arg[4]) - 1
        fnc = arg[0] * exp((arg[1] + arg[2] * y) * y **(1/3))
        return fnc

    return f
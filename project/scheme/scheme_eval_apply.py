import sys

from conda_build.metadata import ensure_valid_fields

from link import *
from scheme_utils import *
from scheme_reader import read_line
from scheme_builtins import create_global_frame
from ucb import main, trace

##############
# Eval/Apply #
##############

def scheme_eval(expr, env, _=None): # Optional third argument is ignored
    """Evaluate Scheme expression EXPR in Frame ENV.

    >>> expr = read_line('(+ 2 2)')
    >>> expr
    Link('+', Link(2, Link(2)))
    >>> scheme_eval(expr, create_global_frame())
    4
    """
    # Evaluate atoms
    if scheme_symbolp(expr):
        return env.lookup(expr)
    elif self_evaluating(expr):
        return expr

    # All non-atomic expressions are lists (combinations)
    if not scheme_listp(expr):
        raise SchemeError('malformed list: {0}'.format(repl_str(expr)))
    first, rest = expr.first, expr.rest

    from scheme_forms import SPECIAL_FORMS # Import here to avoid a cycle when modules are loaded
    if scheme_symbolp(first) and first in SPECIAL_FORMS:
        return SPECIAL_FORMS[first](rest, env)
    else:
        # BEGIN PROBLEM 3
        "*** YOUR CODE HERE ***"
        procedure = scheme_eval(first, env)
        re = map_link(lambda x : scheme_eval(x,env),rest)
        # END PROBLEM 3
        return scheme_apply(procedure, re,env)

def scheme_apply(procedure, args, env):
    """Apply Scheme PROCEDURE to argument values ARGS (a Scheme list) in
    Frame ENV, the current environment."""
    validate_procedure(procedure)
    if not isinstance(env, Frame):
       assert False, "Not a Frame: {}".format(env)
    if isinstance(procedure, BuiltinProcedure):
        # BEGIN PROBLEM 2
        "*** YOUR CODE HERE ***"
        l = []
        while args is not Link.empty:
            l.append(args.first)
            args = args.rest
        if procedure.need_env:
            l.append(env)
        # END PROBLEM 2
        try:
            # BEGIN PROBLEM 2
            "*** YOUR CODE HERE ***"
            return procedure.py_func(*l)
            # END PROBLEM 2
        except TypeError as err:
            raise SchemeError('incorrect number of arguments: {0}'.format(procedure))
    elif isinstance(procedure, LambdaProcedure):
        # BEGIN PROBLEM 9
        "*** YOUR CODE HERE ***"
        # print(f"DEBUG:Lambda{procedure}")
        child = procedure.env.make_child_frame(procedure.formals,args)
        return eval_all(procedure.body, child)
        # END PROBLEM 9
    elif isinstance(procedure, MuProcedure):
        # BEGIN PROBLEM 11
        "*** YOUR CODE HERE ***"
        # print(f"DEBUG:Mu{procedure}")
        child = env.make_child_frame(procedure.formals,args)
        return scheme_eval(procedure.body, child,True)
        # END PROBLEM 11
    else:
        assert False, "Unexpected procedure: {}".format(procedure)

def eval_all(expressions, env):
    """Evaluate each expression in the Scheme list EXPRESSIONS in
    Frame ENV (the current environment) and return the value of the last.

    >>> eval_all(read_line("(1)"), Frame(None))
    1
    >>> eval_all(read_line("(1 2)"), Frame(None))
    2
    """
    # BEGIN PROBLEM 6
    # print(f"DEBUG:{expressions}")
    if expressions is None:
        return None
    x = None
    while expressions is not Link.empty:
        if expressions.rest is Link.empty:
            x = scheme_eval(expressions.first, env, True)
        else:
            x = scheme_eval(expressions.first, env)
        expressions = expressions.rest
    return x


    # END PROBLEM 6

###################################
# Extra Challenge: Tail Recursion #
###################################

class Unevaluated:
    """An expression and an environment in which it is to be evaluated."""

    def __init__(self, expr, env):
        """Expression EXPR to be evaluated in Frame ENV."""
        self.expr = expr
        self.env = env

def complete_apply(procedure, args, env):
    """Apply procedure to args in env; ensure the result is not an Unevaluated."""
    validate_procedure(procedure)
    val = scheme_apply(procedure, args, env)
    if isinstance(val, Unevaluated):
        return scheme_eval(val.expr, val.env)
    else:
        return val

def optimize_tail_calls(unoptimized_scheme_eval):
    """Return a properly tail recursive version of an eval function."""
    def optimized_eval(expr, env, tail=False):
        """Evaluate Scheme expression EXPR in Frame ENV. If TAIL,
        return an Unevaluated containing an expression for further evaluation.
        """
        '''如果是尾调用,并且不是原子 延迟求值'''
        if tail and not scheme_symbolp(expr) and not self_evaluating(expr):
            return Unevaluated(expr, env)

        #否则的化正常求值
        result = Unevaluated(expr, env)
        # BEGIN OPTIONAL PROBLEM 2
        "*** YOUR CODE HERE ***"
        while isinstance(result, Unevaluated):
            result = unoptimized_scheme_eval(result.expr, result.env)
        return result
        # END OPTIONAL PROBLEM 2
    return optimized_eval














################################################################
# Uncomment the following line to apply tail call optimization #
################################################################

scheme_eval = optimize_tail_calls(scheme_eval)

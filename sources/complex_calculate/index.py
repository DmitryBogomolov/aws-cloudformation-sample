import util.mod1 as mod1
import util.mod2 as mod2

def handler(event, context):
    a = event['a']
    b = event['b']
    return {
        '1': mod1.calculate(a, b),
        '2': mod2.calculate(a, b)
    }

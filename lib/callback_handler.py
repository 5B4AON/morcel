import uasyncio as asyncio

__version__ = (0, 2, 0)
# v0.1.0 Outer lambda passes a dictionary of Tasks to inner labda which returns a callback function
# Inner lambda locates a dictionary item based on supplied event argument
# v0.1.1 The item Tasks can have arguments if defined as tuples, first element representing the
# function name and the rest the arguments i.e. (func,arg1,arg2)
# v0.1.2 Dictionary key 'Default' indicates what to do if no key is found for the specified event
# v0.1.3 If Default key is not provided then an empty task list is returned
# v0.1.4 The 'Always' key if provided, defines tasks that will always be executed
# v0.1.5 If an empty dictionary {} is supplied as a tuple argument it gets replaced by the event object
# v0.2.0 Complete rewrite to avoid lambda recursive calls because we are hitting micropython max recursion depth

#r = lambda t,e: [(e if type(x) is dict and len(x) == 0 else x) for x in t]
#x = lambda t,e:(t[0](*r(t[1:],e)) if type(t) is tuple else t())
#f = lambda l,e: l.get(e) if l.get(e) is not None else l.get('Default')
#d = lambda l,e: f(l,e) if f(l,e) is not None else []
#s = lambda l,e: d(l,e) if l.get('Always') is None else d(l,e) + d(l,'Always')
#CallBackHandler = lambda l: lambda e: [x(t,e) for t in s(l,e)]

def CallBackHandler(behaviour):
    def handler(data):
        actions = behaviour.get(data)
        if actions is None:
            actions = behaviour.get('Default')
        if actions is None:
            actions = []
        always = behaviour.get('Always')
        if not always is None:
            actions = actions + always
        for action in actions:
            if type(action) is tuple:
                finalParams = []
                for param in action[1:]:
                   if type(param) is dict and len(param) == 0:
                       finalParams.append(data)
                   else:
                       finalParams.append(param)
                action[0](*finalParams)
            else:
                action()
    return handler



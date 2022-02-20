try:
    import explorerhat
    import json
    print("Import successful")
except:
    print("Import failed")


def changed(input):
  state = input.read()
  name  = input.name
  print("Input {} changed to {}".format(name,state))
  
#explorerhat.input.one.changed(changed)
def readAnalog(value):
    if value == 4:
        return explorerhat.analog.four.read()
    if value == 1:
        return explorerhat.analog.one.read()
    else:
        return 0



"""
while False:
    value1 = explorerhat.analog.one.read()
    value2 = explorerhat.analog.two.read()
    x = {"Heart rate":value1,"Brain waves":value2}
    y = json.dumps(x)
"""

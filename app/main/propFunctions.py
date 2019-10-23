# NOTE: to run tests uncomment propTest() call at end of this file! 

from configobj import ConfigObj
from flask import current_app as app
import json

# for user default settings i.e. port / baud
personalConfig = ConfigObj("./instance/personal.ini")

# for App default settings 
defaultConfig = ConfigObj("./config/default.ini")


def getProperty(store, key, default=None):

    if(store == "personal"):
        storeRef = personalConfig
    elif(store == "default"):
        storeRef = defaultConfig
    else:
        raise Exception("invaild property store specifiec - only 'personal' or 'default' accepted ")
        return

    try:
        # read key from Store
        tmp = storeRef[key]
    except KeyError as ke:
        # key not found- but store exists - return default
        print('Key [' + key + '] does not exist in the [' + store + '] property store, located at ' + storeRef.filename + '!, Retuning default')
        return default
    except Exception as e:
        print("Exception in getPersonalSetting - other Exception")
        print(e)    
    # if no error return value read
    return tmp


def getDictionary(store, key, value):
    print('calling getProperty')
    tmp = getProperty(store, key, value)
    print('returned' + tmp)
    print('converting to json')
    jtmp = json.loads(tmp)
    print('json = ' + json.dumps(jtmp))
    return dict(jtmp)

def setProperty(store, key, value):

    if(store == "personal"):
        storeRef = personalConfig
    elif(store == "default"):
        storeRef = defaultConfig
    else:
        raise Exception("invaild property store specified - only 'personal' or 'default' accepted ")
        return

    try:
        # write value as string ( just in case)
        storeRef[key] = str(value)
        storeRef.write()
    except Exception as e:
        print("Exception")
        print(e)


def propTest():
    print("         ********************************")
    print("         Starting PropTest")
    print("         ********************************")
    
    #config = ConfigObj("instance/config.ini")
    # remove the key first 
    try:
        print("         We are expecting an inccorect store Exception here")
        # test for invaild store specified
        ans2 = getProperty('wrong', 'HOSTKEY', 'FRANK')
        print("         " + ans2)
    except Exception as e3:
        print("         "   + str(e3))

    try:
        personalConfig.pop('HOSTKEY')
    except Exception as e2:
        print("         personalConfig Exception in pop of HOSTKEY")
        print("         " + str(e2))

    print("         personalConfig read for missing key - we Expect to get the default BOB back.")
    ans = getProperty('personal','HOSTKEY', "BOB")
    print("         " + ans)

    # set value 
    print("         Setting value in property file Key HOSTKEY2 we expect to get 'HOSTKEY2_newVal' below...")
    setProperty('personal', 'HOSTKEY2', 'HOSTKEY2_newVal')
    

    print("         " + getProperty('personal', 'HOSTKEY2', "BOB"))
    print("         Setting value in property file Key HOSTKEY2 we expect to get 'HOST_KEY_2' below...")
    setProperty('personal', 'HOSTKEY2', 'HOST_KEY_2')
    print("         " + getProperty('personal', 'HOSTKEY2', "BOB"))

    print("         ********************************")
    print("         End PropTest")
    print("         ********************************")


#propTest()
#import the necessary module!
from plyer import notification

profitFound = True
title = ""
#specify the parameters
#Add code for Arbitrage and set profitFound = True once there is profit
if profitFound:
    title = 'Arbitrage Oppurtunity Found!'
    message = 'Initiate Trading Strategy!'

notification.notify(title= title,
                    message= message,
                    app_icon = None,
                    timeout= 1,
                    toast=False)


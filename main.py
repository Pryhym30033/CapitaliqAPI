from capitaliqSDK import *
import pandas as pd


name = Company_List()

strYear = input("START YEAR: ")
strYearInt = int(strYear)+1

endYear = input("END YEAR: ")
endYearInt = int(endYear)

findata = GetFinData(name[1], strYearInt, endYearInt)
finframe = CashAccum(findata)
revFrame = rev(findata)
rtoic = ROIC(findata)

prices = GetPriceData(name[1], strYear, endYear)
priceframe = PriceAccum(prices)

Plot(name[0], finframe, priceframe, revFrame, rtoic)


report(name[0], rtoic, finframe, revFrame, priceframe)

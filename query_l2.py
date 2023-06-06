import ape
import requests

ape.networks.parse_network_choice('arbitrum:mainnet-fork').__enter__()

## this script runs through the /arbitrum/factory api and checks the stableswaps pools for their `admin_balances`.
poolproxy = ape.Contract("0xd4F94D0aaa640BBb72b5EEc2D85F6D114D81a88E")

# arbitrum curve api
# https://api.curve.fi/api/getPools/arbitrum/main
# https://api.curve.fi/api/getPools/arbitrum/crypto
# https://api.curve.fi/api/getPools/arbitrum/factory

api1 = requests.get("https://api.curve.fi/api/getPools/arbitrum/factory")
api1 = api1.json()
api1 = api1['data']['poolData']
grandTOTAL = 0

for x in api1:
    name = x['name']
    poolADDR = x['address']
    LPTokenADDR = x['lpTokenAddress']
    tokens = x['coins'] # list of the coins in the pool
    
    print("pool: " + poolADDR + " - " + name)

    totalSupply = float(x['totalSupply']) / 1e18
    usdTOTAL = x['usdTotal']
    totalFEES = 0


    # connecting to the pool and token contract
    try:
        poolContract = ape.Contract(poolADDR)
        tokenContract = ape.Contract(LPTokenADDR)
    except:
        pass

    # fee receiver of the contract
    try:    
        try:
            feeReceiver = poolContract.admin_fee_receiver()
        except:
            feeReceiver = poolContract.owner()
        if feeReceiver != '0xd4F94D0aaa640BBb72b5EEc2D85F6D114D81a88E':
            print("WARNING: fee receiver is not PoolProxy!")
        else:
            pass
    except:
        pass


        # owner of the contract
    try:
        owner = poolContract.owner()
        print("owner: " + owner)
        print("")
    except:
        print("ERROR: check facotry")
        print("")


    # get admin balances of the pools
    totalUSD = 0
    try:
        if len(tokens) == 2:
            p0 = tokens[0]['usdPrice']
            d0 = float(tokens[0]['decimals'])
            p1 = tokens[1]['usdPrice']
            d1 = float(tokens[1]['decimals'])
            admin_balance0 = poolContract.admin_balances(0)
            admin_balance1 = poolContract.admin_balances(1)
            tokenAmount0 = admin_balance0 / 10 ** d0
            tokenAmount1 = admin_balance1 / 10 ** d1
            tokenValue0 = tokenAmount0 * p0
            tokenValue1 = tokenAmount1 * p1
            sum = tokenValue0 + tokenValue1
            totalUSD += sum
            print(tokenValue0)
            print(tokenValue1)
            
        elif len(tokens) == 3:
            p0 = tokens[0]['usdPrice']
            d0 = float(tokens[0]['decimals'])
            p1 = tokens[1]['usdPrice']
            d1 = float(tokens[1]['decimals'])
            p2 = tokens[2]['usdPrice']
            d2 = float(tokens[2]['decimals'])
            admin_balance0 = poolContract.admin_balances(0)
            admin_balance1 = poolContract.admin_balances(1)
            admin_balance2 = poolContract.admin_balances(2)
            tokenAmount0 = admin_balance0 / 10 ** d0
            tokenAmount1 = admin_balance1 / 10 ** d1
            tokenAmount2 = admin_balance2 / 10 ** d2
            tokenValue0 = tokenAmount0 * p0
            tokenValue1 = tokenAmount1 * p1
            tokenValue2 = tokenAmount2 * p2
            sum = tokenValue0 + tokenValue1 + tokenValue2
            totalUSD += sum
            print(tokenValue0)
            print(tokenValue1)
            print(tokenValue2)

        elif len(tokens) == 4:
            p0 = tokens[0]['usdPrice']
            d0 = float(tokens[0]['decimals'])
            p1 = tokens[1]['usdPrice']
            d1 = float(tokens[1]['decimals'])
            p2 = tokens[2]['usdPrice']
            d2 = float(tokens[2]['decimals'])
            p3 = tokens[3]['usdPrice']
            d3 = float(tokens[3]['decimals'])
            admin_balance0 = poolContract.admin_balances(0)
            admin_balance1 = poolContract.admin_balances(1)
            admin_balance2 = poolContract.admin_balances(2)
            admin_balance3 = poolContract.admin_balances(3)
            tokenAmount0 = admin_balance0 / 10 ** d0
            tokenAmount1 = admin_balance1 / 10 ** d1
            tokenAmount2 = admin_balance2 / 10 ** d2
            tokenAmount3 = admin_balance3 / 10 ** d3
            tokenValue0 = tokenAmount0 * p0
            tokenValue1 = tokenAmount1 * p1
            tokenValue2 = tokenAmount2 * p2
            tokenValue3 = tokenAmount3 * p3
            sum = tokenValue0 + tokenValue1 + tokenValue2 +tokenValue3
            totalUSD += sum
            print(tokenValue0)
            print(tokenValue1)
            print(tokenValue2)
            print(tokenValue3)
        else:
            pass
    except:
        print("error")
    
    try:
        xcp_profit = poolContract.xcp_profit()
        xcp_profit_a = poolContract.xcp_profit_a()
        vprice = poolContract.virtual_price()
        admin_fee = poolContract.admin_fee()


        # claim (frac) calc
        if xcp_profit > xcp_profit_a:
            fees = (xcp_profit - xcp_profit_a) * admin_fee / (2 * 10**10)
            msgFEE = f'''fees: {fees}'''
            print(msgFEE)
            if fees > 0:
                frac = vprice * 10**18 / (vprice - fees) - 10**18
                msgFRAC = f'''frac: {frac}'''
                print(msgFRAC)
                ## mint calc
                frac1 = frac / 1e18
                supply = tokenContract.totalSupply() / 1e18
                d_supply = supply * frac1
                if d_supply > 0:
                    usdVALUE = d_supply * (usdTOTAL / totalSupply)
                    totalUSD += usdVALUE
                    print("claimable lp tokens: " + d_supply + "; approx usd value: " + usdVALUE)
                else: 
                    print("minted supply <= 0")
            else:
                print("xcp_profit < xcp_profit_a!") # does this mean the pool did not make enough profit yet?
    except:
        pass


    grandTOTAL += totalUSD

    print("unclaimed fees from pool: " + str(totalUSD))

    print("")
    print("POOLPROXY BALANCES & BURNERS:")

    # burners
    # somehow api does not always return the lp token symbol? why?
    try:
        lpSymbol = x['symbol']
        burnerLP = poolproxy.burners(LPTokenADDR)
        if burnerLP == '0x0000000000000000000000000000000000000000':
            print("NO BURNER (LP TOKEN): " + lpSymbol)
    except:
        pass

    for x in tokens:
        coinSYMBOL = x['symbol']
        coinADDR = x['address']
        burner = poolproxy.burners(coinADDR)
        if burner == '0x0000000000000000000000000000000000000000':
            print("NO BURNER: " + coinSYMBOL)
    
    try:
        LPTokenContract = ape.Contract(LPTokenADDR)
        LPbalanceInFeeReceiver = LPTokenContract.balanceOf("0xd4F94D0aaa640BBb72b5EEc2D85F6D114D81a88E") / 10**18
        print(lpSymbol + ": " + str(LPbalanceInFeeReceiver))
    except:
        pass

    for x in tokens:
        try:
            coinSYMBOL = x['symbol']
            coinADDR = x['address']
            coinDECIMAL = float(x['decimals'])
            coinContract = ape.Contract(coinADDR)
            balanceInFeeReceiver = coinContract.balanceOf("0xd4F94D0aaa640BBb72b5EEc2D85F6D114D81a88E") / 10**coinDECIMAL
            print(coinSYMBOL + ": " + str(balanceInFeeReceiver))
        except:
            print("ERROR!")

    print("")
    print("------------------")
    print("")


print("TOTAL UNCLAIMED ADMIN FEES FROM ALL POOLS: " + str(grandTOTAL))
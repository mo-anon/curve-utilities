import ape
import requests

# connecting to eth mainnet
ape.networks.parse_network_choice('ethereum:mainnet-fork').__enter__()
    
# connecting to contracts
metaregistry = ape.Contract("0xF98B45FA17DE75FB1aD0e7aFD971b0ca00e379fC")
ecb = ape.Contract("0xeCb456EA5365865EbAb8a2661B0c503410e9B347")
print("------")


# ethereum curve api
# https://api.curve.fi/api/getPools/ethereum/main
# https://api.curve.fi/api/getPools/ethereum/crypto
# https://api.curve.fi/api/getPools/ethereum/factory
# https://api.curve.fi/api/getPools/ethereum/factory-crypto

def main(api_url):
    api1 = requests.get(api_url)
    api1 = api1.json()
    api1 = api1['data']['poolData']
    grandTOTAL = 0


    for x in api1:
        name = x['name']
        poolADDR = x['address']
        LPTokenAddr = x['lpTokenAddress']
        tokens = x['coins'] # list of the coins in the pool
        print("pool: " + poolADDR + " - " + name)

        poolContract = ape.Contract(poolADDR)

        # fee receiver of the contract
        try:    
            try:
                feeReceiver = poolContract.admin_fee_receiver()
            except:
                feeReceiver = poolContract.owner()

            if feeReceiver != '0xeCb456EA5365865EbAb8a2661B0c503410e9B347':
                print("WARNING: fee receiver is not 0xecb!")
            else: 
                pass
        except:
            pass

        # owner of the contract
        try:
            try:
                owner = poolContract.owner()
                print("owner: " + owner)
                print("")
            except:
                admin = poolContract.admin()
                print("admin: " + admin)
                print("")
        except:
            print("ERROR: NO ADMIN OR OWNER")
            print("")


        # get admin_balances of the pool. there must be an easier way to do this????
        totalUSD = 0
        admin_balances = metaregistry.get_admin_balances(poolADDR)
        admin_balances = admin_balances[:len(tokens)]
        symbols = [token['symbol'] for token in tokens]
        usdPrice = [token['usdPrice'] for token in tokens] or 0
        decimals = [token['decimals'] for token in tokens]

        # this is to avoid failing because price of some tokens is "null". look for another fix!
        try:
            for (a, b, c, d) in zip(admin_balances, symbols, usdPrice, decimals):
                tokenAmount = a / 10**float(d)
                usdVaule = tokenAmount * c
                totalUSD += usdVaule
                print(b + ": " + str(usdVaule))
        except:
            pass

        grandTOTAL += totalUSD
        print("total unclaimed fees (usd): " + str(totalUSD))

        print("")
        print("POOLPROXY BALANCES & BURNERS:")


        # burners
        # somehow api does not always return the lp token symbol? why?
        try:
            lpSymbol = x['symbol']
            burnerLP = ecb.burners(LPTokenAddr)
            if burnerLP == '0x0000000000000000000000000000000000000000':
                print("NO BURNER (LP TOKEN): " + lpSymbol)
        except:
            pass

        for x in tokens:
            coinSYMBOL = x['symbol']
            coinADDR = x['address']
            burner = ecb.burners(coinADDR)
        
            if burner == '0x0000000000000000000000000000000000000000':
                print("NO BURNER: " + coinSYMBOL)


        # query how much tokens of the pools sit in the fee_receiver and need to be burned
        try:
            LPTokenContract = ape.Contract(LPTokenAddr)
            LPbalanceInFeeReceiver = LPTokenContract.balanceOf("0xeCb456EA5365865EbAb8a2661B0c503410e9B347") / 10**18
            print(lpSymbol + ": " + str(LPbalanceInFeeReceiver))
        except:
            print("error")

        for x in tokens:
            try:
                coinSYMBOL = x['symbol']
                coinADDR = x['address']
                coinDECIMAL = float(x['decimals'])
                coinContract = ape.Contract(coinADDR)
                balanceInFeeReceiver = coinContract.balanceOf("0xeCb456EA5365865EbAb8a2661B0c503410e9B347") / 10**coinDECIMAL
                print(coinSYMBOL + ": " + str(balanceInFeeReceiver))
            except:
                print("ERROR!")

        print("")
        print("------------------")
        print("")




    print("TOTAL UNCLAIMED FEES: " + str(grandTOTAL))


main("https://api.curve.fi/api/getPools/ethereum/main")
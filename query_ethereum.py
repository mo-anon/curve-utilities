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
        except:
            pass

        if feeReceiver != '0xeCb456EA5365865EbAb8a2661B0c503410e9B347':
            print("WARNING: fee receiver is not 0xecb!")
        else: 
            pass


        # owner of the contract
        try:
            owner = poolContract.owner()
            print("owner: " + owner)
            print("")
        except:
            print("ERROR: NO OWNER")
            print("")


        # get admin_balances of the pool. there must be an easier way to do this????
        totalUSD = 0
        admin_balances = metaregistry.get_admin_balances(poolADDR)

        if len(tokens) == 2:
            s0 = tokens[0]['symbol']
            s1 = tokens[1]['symbol']
            p1 = tokens[1]['usdPrice'] or 0
            p0 = tokens[0]['usdPrice'] or 0
            d0 = float(tokens[0]['decimals'])
            d1 = float(tokens[1]['decimals'])
            balance0 = admin_balances[0] / 10**d0
            balance1 = admin_balances[1] / 10**d1
            balance0usd = balance0 * p0
            balance1usd = balance1 * p1
            print(s0 + ": " + str(balance0))
            print(s1 + ": " + str(balance1))
            totaUnclaimedUSD = balance0usd + balance1usd
            totalUSD += totaUnclaimedUSD
            grandTOTAL += totaUnclaimedUSD


        elif len(tokens) == 3:
            s0 = tokens[0]['symbol']
            s1 = tokens[1]['symbol']
            s2 = tokens[2]['symbol']
            p0 = tokens[0]['usdPrice'] or 0
            p1 = tokens[1]['usdPrice'] or 0
            p2 = tokens[2]['usdPrice'] or 0
            d0 = float(tokens[0]['decimals'])
            d1 = float(tokens[1]['decimals'])
            d2 = float(tokens[2]['decimals'])
            balance0 = admin_balances[0] / 10**d0
            balance1 = admin_balances[1] / 10**d1
            balance2 = admin_balances[2] / 10**d2
            balance0usd = balance0 * p0
            balance1usd = balance1 * p1
            balance2usd = balance2 * p2
            print(s0 + ": " + str(balance0))
            print(s1 + ": " + str(balance1))
            print(s2 + ": " + str(balance2))
            totaUnclaimedUSD = balance0usd + balance1usd + balance2usd
            totalUSD += totaUnclaimedUSD
            grandTOTAL += totaUnclaimedUSD
                    
        elif len(tokens) == 4:
            s0 = tokens[0]['symbol']
            s1 = tokens[1]['symbol']
            s2 = tokens[2]['symbol']
            s3 = tokens[3]['symbol']
            p0 = tokens[0]['usdPrice'] or 0
            p1 = tokens[1]['usdPrice'] or 0
            p2 = tokens[2]['usdPrice'] or 0
            p3 = tokens[3]['usdPrice'] or 0
            d0 = float(tokens[0]['decimals'])
            d1 = float(tokens[1]['decimals'])
            d2 = float(tokens[2]['decimals'])
            d3 = float(tokens[3]['decimals'])
            balance0 = admin_balances[0] / 10**d0
            balance1 = admin_balances[1] / 10**d1
            balance2 = admin_balances[2] / 10**d2
            balance3 = admin_balances[3] / 10**d3
            balance0usd = balance0 * p0
            balance1usd = balance1 * p1
            balance2usd = balance2 * p2
            balance3usd = balance3 * p3
            print(s0 + ": " + str(balance0))
            print(s1 + ": " + str(balance1))
            print(s2 + ": " + str(balance2))
            print(s3 + ": " + str(balance3))
            totaUnclaimedUSD = balance0usd + balance1usd + balance2usd + balance3usd
            totalUSD += totaUnclaimedUSD
            grandTOTAL += totaUnclaimedUSD
        else:
            print("error. pls check")

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
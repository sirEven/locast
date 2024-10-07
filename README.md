<div align="center">
    <img src="locast@3x.png" alt="alt text" width="200" height="200">
</div>
LoCaSt: Local Candle Store - A module to download and store price candles from exchanges in a database.

# Intro
LoCaSt handles candle data in a very straight forward manner: 
- there is one underlying `Candle` type to hold the relevant data of a price candle
- a group of such `Candle` objects is collected into a **cluster**, which is simply a `List[Candle]`
- these clusters are written into an sqlite database an can be updated as needed

### Cluster
A cluster is a list of candle objects, representing a time series of price data. Per exchange, market and resolution, there can be exactly one cluster in the database. It can be interacted with in the following ways.

### Currently implemented

#### Features
- create cluster
- retrieve cluster 
- update cluster 
- delete cluster
- get info about cluster
    - head
    - tail 
    - amount of candles
    - wether it is up to date
- ... more to come

#### Exchanges
- dydx (v3)
- dydx v4
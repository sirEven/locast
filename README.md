<table>
  <tr>
    <td align="center"><img src="icons/deprecated_icon@3x.png" alt="" width="200"></td>
    <td align="center"><img src="icons/color_black_white@3x.png" alt="" width="200"></td>
    <td align="center"><img src="icons/color_transparent_1@3x.png" alt="" width="200"></td>
    
  </tr>
  <tr>
    <td align="center"><img src="icons/color_transparent_2@3x.png" alt="" width="200"></td>
    <td align="center"><img src="icons/fancy_transparent@3x.png" alt="" width="200"></td>
    <td align="center"><img src="icons/grey_1@3x.png" alt="" width="200"></td>
  </tr>
  <tr>
    <td align="center"><img src="icons/grey_2@3x.png" alt="" width="200"></td>
    <td align="center"><img src="icons/grey_transparent_1@3x.png" alt="" width="200"></td>
    <td align="center"><img src="icons/grey_transparent_2@3x.png" alt="" width="200"></td>
  </tr>
  <tr>
    <td align="center"><img src="icons/halloween_1@3x.png" alt="" width="200"></td>
    <td align="center"><img src="icons/halloween_2@3x.png" alt="" width="200"></td>
    <td align="center"><img src="icons/halloween_3@3x.png" alt="" width="200"></td>
  </tr>
</table>

LoCaSt: Local Candle Store - A module to download price candles from exchanges and store them in a database.

# Intro
LoCaSt handles candle data in a very straight forward manner: 
- There is one underlying `Candle` type to hold the relevant data of a price candle.
- A group of such `Candle` objects is collected into a **cluster**, which is simply a `List[Candle]`.
- These clusters are written into an sqlite database and can be updated as needed.

### Cluster
A cluster is a list of candle objects, representing a time series of price data. Per exchange, market and resolution, there can be exactly one cluster in the database. It can be interacted in the following ways.

### Currently implemented

#### Features
- Create cluster
- Retrieve cluster 
- Update cluster 
- Delete cluster
- Get info about cluster
    - head
    - tail 
    - amount of candles
    - wether it is up to date or not
- ... more to come

#### Exchanges
- dydx (v3)
- dydx v4
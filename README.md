<div align="center"><img src="icons/halloween_3@3x.png" alt="" width="200"></td></div>
<b><center>LoCaSt</center></b>

Local Candle Store - A module to download price candles from exchanges and store them in a database.

# Intro
LoCaSt handles candle data in a very straight forward manner: 
- There is one underlying `Candle` type to hold the relevant data of a price candle.
- A group of such `Candle` objects is collected into a **cluster**, which is simply a `List[Candle]`.
- These clusters are written into an sqlite database and can be updated as needed.

## Cluster
A cluster is a list of candle objects, representing a time series of price data. Per exchange, market and resolution, there can be exactly one cluster in the database. It can be interacted in the following ways.

## Currently implemented

### Features
- Create cluster
- Retrieve cluster 
- Update cluster 
- Delete cluster
- Get info about cluster
    - newest candle
    - oldest 
    - size of cluster (amount of candles it entails)
    - wether it is up to date or not
- ... more to come

### Exchanges
- dydx (v3)
- dydx v4

### Storage Technologies
- Sqlite

# Collaboration
Here are some ideas and guidelines for collaboration.

## Goals
- Implement additional exchanges 
- Implement additional storage technologies, if necessary
- Improve code quality and maintainability

## Branches
There are two branches:
- Main: 
    - Expects pull requests from collaborators.
    - Pushing will trigger a unit test workflow
- Release: 
    - Is handled by maintainer to merge main into and update release number
    - Pushing will trigger the same unit test workflow and additionally publish to pypi.org

## Code
This project tries to maintain readable and simple code.

Basic principles like DRY and separation of concerns are mandatory - but following patterns dogmatically is not desired at all.

In fact this project shall be a collaborative effort in which developers interested in it, can learn from each other and discuss their ideas and solutions to. Besides, of course, being a tool for anybody who needs candle data available locally, without the hassle of talking to exchange APIs.

To collaborate, just make pull requests on main.

There are # COLLABORATION markers throughout the test suite to mark and explain places that are relevant for new implementations. The general idea is to not require new implementations to come up with their unit and/or integration tests, but rather include their mock and production implementations through parametrization and fixtures in the existing test suite. 

Of course if new test cases are necessary, they most certainly should be implemented for all existing implementations as well. 
This has the advantage of not having to write tests again and again but also enforces the behavior of new implemntations to be identical to existing ones. 

For example if we implement a new candle fetcher for the 1inch API, it can be implemented in what ever way is best - but it should behave exactly the same as the existing dydx implementations, which is enforced by the parametrized test suite.
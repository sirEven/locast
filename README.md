LoCaSt: Local Candle Store - A module to download and store price candles from exchanges in a database. 
LiveCandle: Experimental feature that will probably be extracted from here at some point.

Glue Project Thoughts & Ideas:
The idea is to have the live candle turn on at the begining of execution, either by itself within init, or by the glue project that calls its start function (and stop function at shut down). 
What can be considered unnecessary is dynamic subscribing and unsubscribing to certain markets - instead we could pause
publishing those candles if desired. But even that might be unnecessary. We should think about what exactly we would want to pause, once a position has beend opened. Naturally we would keep candles being created and published but would simply stop forming fresh predictions. Important: LiveCandle will NOT be used to feed into Candle Store. 
CandleFetcher:
The component that fetches historic candles (create a cluster of candles) in order to store them into a db so they don't have to be downloaded again in the future. 

Glue Project conisderations: 
The orchestration of these functionalities would be implemented in glue project, meaning Locast only has very rudimentary API methods:
- create cluster (CandleFetcher)
- update cluster (CandleFetcher)
- start live candle (LiveCandle)
- stop live candle (LiveCandle)

This guarantees, that it can be reused in model training project as well where different glue code is needed but same basic functionality.
For example: create / update clusters, train models. Whereas glue project would want to just start a live candle and feed it into prediction module.
Later on maybe have glue code updated to incorporate some sort of regular update of clusters (every n resolutions), retrain models etc, such that prediction module always loads the latest trained model before performing predictions.
These can be thought of as different routines: 
Routines: 
- Training
    - Create/update cluster
    - Train model
    - Update model
- Predicting
    - Receive newest candle
    - Load model
    - Predict price
- Trading
    - Receive predictions
    - check positions
    - open positions

Glue Project will eventually orchestrate these, but they can be executed individually by hand as well.

Training simply accesses the db stored candles - wether they are up to date or not is not of interest to it (that needs to be guaranteed by glue orchestration). Training also checks if a model with recent enough training date exists, if yes, ommit training a new one (except a force flag is passed). 

Predicting simply accesses db stored models - per exchange, market and resolution there will be one single entry (or none, which would error out) that is used to 
perform predictions

Trading simply receives a prediction and checks open position of that market, if it does not exist, it will open a new one based on the prediction.
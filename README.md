# Telegram Bot - Storj Node Monitor

If you have a [Storj Node](https://storj.io/storage-node-operator), You can implement this telegram bot to check all the statistics of your node and you can also receive notifications in case your node goes down.
The statistics that you can see are the same as in the Dashboard of your Storj Node. From this bot you will be able to consult the statistics of all your Storj nodes, there is no need for a bot for each node.


You can try the bot [here](t.me/storjnodemonitor_bot).

But they can also implement within your infrastructure very easily, below you have a guide.

# Get Started

This Bot is mounted on Docker, so implementing it is very easy. You just need to have a database [MongoDB 4.2.6-bionic](https://hub.docker.com/_/mongo) and this container.

> It is important that the database with your username and password are previously created before launching the bot.

## Environment variables
Below you can see the Environment variables necessary for the operation of this container.

 - **$TELEGRAM_TOKEN** -> Token to access the HTTP API of your bot. 
 
 - **$URI_MONGODB**	-> Connection URI with your MongoDB database. 
 
> For example: mongodb://user:pass@192.168.1.2/botstorjmonitor


## Start the Container

To run this bot using Docker you can use the following command:

    docker run -d \
    -e "TELEGRAM_TOKEN=YOUR-TELEGRAM-TOKEN" \
    -e "URI_MONGODB=YOUR_URI_CONNECT_MONGODB"
    rafa93m/bot-storjnodemonitor

Once this is done, you can now speak with your bot from the Telegram APP.

## Donations

**ETH**: 0xF47FB0A777881545ED7b97B289961e78e97Aa760



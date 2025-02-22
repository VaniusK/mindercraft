const WebSocket = require('ws');
const mineflayer = require('mineflayer');
const { Vec3 } = require('vec3');
const { pathfinder, Movements, goals } = require('mineflayer-pathfinder');


const wss = new WebSocket.Server({ port: 3000 });
let wsClient = null;


const options = {
    host: process.argv[process.argv.indexOf('--host') + 1],
    port: parseInt(process.argv[process.argv.indexOf('--port') + 1]),
    version: process.argv[process.argv.indexOf('--version') + 1],
    username: process.argv[process.argv.indexOf('--username') + 1]
};

const bot = mineflayer.createBot(options);

bot.loadPlugin(pathfinder);

bot.once('spawn', () => {

    const mcData = require('minecraft-data')(bot.version);
    const defaultMove = new Movements(bot, mcData);
    bot.pathfinder.setMovements(defaultMove);

});

wss.on('connection', (ws) => {
    bot.chat("Привет");
    wsClient = ws;

    ws.on('message', async (data) => {
        try {
            const command = JSON.parse(data);
            if (command.type === 'chat') {
                bot.chat(command.message);
            } else if (command.type === 'go_to_player') {
                const target = bot.players[command.player_name]?.entity;
                if (target) {
                    const distance = parseFloat(command.distance);
                    const destination = target.position;
                    try {
                        await bot.pathfinder.goto(new goals.GoalNear(destination.x, destination.y, destination.z, distance));
                        if (wsClient) {
                            wsClient.send(JSON.stringify({
                                type: "result",
                                status: "success"
                            }));
                        }
                    } catch (error) {
                        if (wsClient) {
                            wsClient.send(JSON.stringify({
                                type: "result",
                                status: "error"
                            }));
                        }
                    }
                } else {
                    if (wsClient) {
                        wsClient.send(JSON.stringify({
                            type: "result",
                            status: "error",
                            reason: "Couldn't find the player"
                        }));
                    }
                }
            }
        } catch (error) {
            if (wsClient) {
                wsClient.send(JSON.stringify({
                    type: "result",
                    status: "error",
                    reason: "Couldn't parse the command"
                }));
            }
        }
    });
    ws.on('close', () => {
        wsClient = null;
    });
});

// Отправка чата в Python
bot.on('chat', (username, message) => {
    if (wsClient) {
        wsClient.send(JSON.stringify({ type: "chat", role: username, content: message }));
    }
});

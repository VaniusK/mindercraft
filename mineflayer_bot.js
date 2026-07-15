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

async function send_chat(message, function_call_id) {
    bot.chat(message);
    wsClient.send(JSON.stringify({
        type: "result",
        id: function_call_id,
        role: "tool",
        content: JSON.stringify({
            action: "send_chat",
            result: "success"
        })
    }));
}

async function go_to_player(player_name, given_distance, function_call_id) {
    const target = bot.players[player_name]?.entity;
    if (target) {
        const distance = parseFloat(given_distance);
        const destination = target.position;
        try {
            await bot.pathfinder.goto(new goals.GoalNear(destination.x, destination.y, destination.z, distance));
            wsClient.send(JSON.stringify({
                type: "result",
                id: function_call_id,
                role: "tool",
                content: JSON.stringify({
                    action: "go_to_player",
                    result: "success"
                })
            }));
        } catch (error) {
            wsClient.send(JSON.stringify({
                type: "result",
                id: function_call_id,
                role: "tool",
                content: JSON.stringify({
                    action: "go_to_player",
                    result: "error",
                    reason: "Couldn't reach the player"
                })
            }));
        }
    } else {
        wsClient.send(JSON.stringify({
            type: "result",
            id: function_call_id,
            role: "tool",
            content: JSON.stringify({
                action: "go_to_player",
                result: "error",
                reason: "Couldn't find the player"
            })
        }));
    }
}

async function give_item(player_name, item_type, count, function_call_id) {
    const player = bot.players[player_name];
    if (player) {
        await bot.lookAt(player.entity.position.offset(0, 1.6, 0));
    }
    const items = bot.inventory.items().filter(item => item.type === item_type);

    const have_count = items.reduce((sum, item) => sum + item.count, 0);
    if (have_count >= count) {
        await bot.toss(item_type, null, count);
        wsClient.send(JSON.stringify({
            type: "result",
            id: function_call_id,
            role: "tool",
            content: JSON.stringify({
                action: "give_item",
                result: "success"
            })
        }));
    } else {
        wsClient.send(JSON.stringify({
            type: "result",
            id: function_call_id,
            role: "tool",
            content: JSON.stringify({
                action: "give_item",
                result: "error",
                reason: "Don't have enough items"
            })
        }));
    }
}

wss.on('connection', (ws) => {
    wsClient = ws;

    ws.on('message', async (data) => {
        const command = JSON.parse(data);
        if (command.type === 'chat') {
            await send_chat(command.message, command.id);
        } else if (command.type === 'go_to_player') {
            await go_to_player(command.player_name, command.distance, command.id);
        } else if (command.type === 'give_item') {
            await give_item(command.player_name, command.item_type, command.count, command.id);
        }
    });
    ws.on('close', () => {
        wsClient = null;
    });
});

bot.on('chat', (username, message) => {
    wsClient.send(JSON.stringify({ type: "chat", sender: username, role: "user", content: username + " sent chat message: \"" + message + "\"" }));
});

function on_inventory_update() {
    const items = bot.inventory.items();
    if (wsClient) {
        wsClient.send(JSON.stringify({ type: "inventory", content: items }));
    }
}

bot.once('spawn', () => {

    const mcData = require('minecraft-data')(bot.version);
    const defaultMove = new Movements(bot, mcData);
    bot.pathfinder.setMovements(defaultMove);
    on_inventory_update();
    bot.inventory.on('updateSlot', (slot, oldItem, newItem) => {
        on_inventory_update();
    });

});
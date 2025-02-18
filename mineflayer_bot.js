const mineflayer = require('mineflayer');
const { Vec3 } = require('vec3');
const { pathfinder, Movements, goals } = require('mineflayer-pathfinder');

process.on('uncaughtException', (err) => {
    console.error('Uncaught Exception:', err);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection:', reason);
});


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

bot.on('kicked', (reason) => {
    console.error(`Bot was kicked: ${reason}`);
    process.exit(1);
});

bot.on('error', (err) => {
    console.error('Bot error:', err);
    process.exit(1);
});

bot.on('chat', (username, message) => {
    //if (username === bot.username) return; // Не записываем свои сообщения
    const chatMessage = {
        role: username,
        content: message
    };
    console.log(JSON.stringify(chatMessage));
});

process.stdin.setEncoding('utf8');

process.stdin.on('data', (data) => {
    try {
        const command = JSON.parse(data.toString());

        if (command.type === 'chat') {
            bot.chat(command.message);
        } else if (command.type === 'go_to_player') {
            const target = bot.players[command.player_name]?.entity;
            if (target) {
                const distance = parseFloat(command.distance);
                const destination = target.position
                bot.pathfinder.goto(new goals.GoalNear(destination.x, destination.y, destination.z, distance), (err) => {
                    if (err) {
                        console.error('Error navigating:', err);
                        console.log("Navigation result: error"); // Сообщаем об ошибке
                    } else {
                        console.log("Navigation result: success"); // Сообщаем об успехе
                    }
                });

            } else {
                console.error(`Player ${command.player_name} not found.`);
                console.log("Navigation result: error"); // Игрок не найден
            }
        }
        else if (command.type === 'get_position') {
            const player = bot.players[command.player_name];
            if (player && player.entity) {
                const pos = player.entity.position;
                console.log(`Player position: x=${pos.x}, y=${pos.y}, z=${pos.z}`);
            } else {
                console.error(`Player ${command.player_name} not found or has no entity.`);
            }
        }
        else {
            console.error('Unknown command:', command);
        }
    } catch (error) {
        console.error('Error parsing command:', error);
    }
});
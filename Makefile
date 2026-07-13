run_server:
	cd server && java -Xmx4G -Xms4G -jar server.jar nogui
install_dependencies:
	npm install ws mineflayer vec3 mineflayer-pathfinder minecraft-data
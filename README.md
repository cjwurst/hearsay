# Hearsay 
A Python framework motivated by the entity-component-system design pattern. Prioritizes easy testing: Each piece of game logic is isolated in a “component” with no strict dependencies on other components. Game state is made persistent by implementing all events as reversible commands - game state can be rolled back and forward arbitrarily during runtime. 

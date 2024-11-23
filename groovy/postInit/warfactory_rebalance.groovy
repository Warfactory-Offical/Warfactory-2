// Steam age Nuke
// PBF Rebalancing
mods.gregtech.compressor.removeByInput(4, [metaitem('dustFireclay')], null)
furnace.removeByOutput(item('gregtech:meta_item_1', 352))
crafting.removeByOutput(metaitem('dustFireclay'))
furnace.recipeBuilder()
        .input(metaitem('dustFireclay'))
        .output(metaitem('brick.fireclay'))
        .exp(0.5)
        .register()
crafting.shapelessBuilder()
        .output(metaitem('dustFireclay') * 16)
        .input([metaitem('dustClay'),metaitem('dustBrick')])
        .register()

// Wrought Iron Rebalance
furnace.recipeBuilder()
        .input(item('minecraft:iron_ingot'))
        .output(metaitem('ingotWroughtIron'))
        .exp(0.5)
        .register()

// Vacuum Tubes Rebalance
crafting.shapedBuilder()
        .output(metaitem('component.glass.tube'))
        .row('   ')
        .row('000')
        .row('000')
        .key('0', item('minecraft:glass_pane'))
        .register()

// Circuit Board Rebalance
crafting.shapedBuilder()
        .output(metaitem('board.coated'))
        .row('111')
        .row('000')
        .row('111')
        .key('0', ore('plankWood'))
        .key('1', metaitem('rubber_drop'))
        .register()

// Red Alloy Cable Rebalance
crafting.shapelessBuilder()
        .output(metaitem('dustRedAlloy'))
        .input([metaitem('dustCopper'),item('minecraft:redstone'),item('minecraft:redstone'),item('minecraft:redstone'),item('minecraft:redstone')])
        .register()
crafting.shapedBuilder()
        .output(metaitem('plateRubber'))
        .row(' 0 ')
        .row(' 1 ')
        .row(' 1 ')
        .key('0', ore('toolHammer'))
        .key('1', metaitem('rubber_drop'))
        .register()
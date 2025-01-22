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

// Heat Exchanger
crafting.remove('gregtech:heat_exchanger')
crafting.shapedBuilder().name('heat_exchanger')
        .output(metaitem('heat_exchanger'))
        .matrix('GGG', 'HPH', 'GGG')
        .key('G', item('gregtech:metal_casing', 4))
        .key('P', item('gregtech:meta_item_1', 516))
        .key('H', item('gregtech:fluid_pipe_large', 324))
        .register()
//LBF recipes
recipemap('large_blast_furnace').recipeBuilder()
        .inputs(item('minecraft:coal') * 2)
        .inputs(item('minecraft:iron_ingot') * 1)
        .fluidOutputs(fluid('steel') * 144)
        .duration(40)
        .buildAndRegister();

recipemap('strand_caster').recipeBuilder()
        .inputs(item('minecraft:coal') * 2)
        .inputs(item('minecraft:iron_ingot') * 1)
        .fluidOutputs(fluid('steel') * 144)
        .duration(40)
        .buildAndRegister();
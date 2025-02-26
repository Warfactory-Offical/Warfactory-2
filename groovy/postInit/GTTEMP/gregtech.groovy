
// Voiding Cover (Fluid)
crafting.remove('gregtech:cover_fluid_voiding')

mods.gregtech.assembler.removeByInput(30, [
    metaitem('screwSteel') * 2,
    metaitem('cover.fluid.detector'),
    metaitem('pipeNormalFluidBronze'),
    item('minecraft:ender_pearl')
], null)
mods.gregtech.arc_furnace.removeByInput(30, [
    metaitem('cover.fluid.voiding')
], [fluid('oxygen') * 241])
mods.gregtech.macerator.removeByInput(8, [
    metaitem('cover.fluid.voiding')
], null)

recipemap('assembler').recipeBuilder()
    .inputs(ore('screwSteel') * 2)
    .inputs(metaitem('cover.fluid.detector'))
    .inputs(metaitem('pipeNormalFluidBronze'))
    .outputs(metaitem('cover.fluid.voiding'))
    .duration(100).EUt(30).buildAndRegister();

// Voiding Cover (Item)
crafting.remove('gregtech:cover_item_voiding')

mods.gregtech.assembler.removeByInput(30, [
    metaitem('screwSteel') * 2,
    metaitem('cover.item.detector'),
    metaitem('pipeNormalItemBrass'),
    item('minecraft:ender_pearl')
], null)
mods.gregtech.arc_furnace.removeByInput(30, [
    metaitem('cover.item.voiding')
], [fluid('oxygen') * 202])
mods.gregtech.macerator.removeByInput(8, [
    metaitem('cover.item.voiding')
], null)

recipemap('assembler').recipeBuilder()
    .inputs(ore('screwSteel') * 2)
    .inputs(metaitem('cover.item.detector'))
    .inputs(metaitem('pipeNormalItemBrass'))
    .outputs(metaitem('cover.item.voiding'))
    .duration(100).EUt(30).buildAndRegister();

//Regate Multismelter to LV
crafting.shapedBuilder().name('multifurnace')
        .output(metaitem('multi_furnace'))
        .matrix('FFF', 'CHC', 'PCP')
        .key('F', item('minecraft:furnace'))
        .key('C', ore('circuitLv'))
        .key('H', item('gregtech:metal_casing', 2))
        .key('P', metaitem('cableGtSingleTin'))
        .register()


//Distillation Trollage
crafting.remove('gcyl:gcyl_distillation_tower')
crafting.shapedBuilder().name('distillationtowerrecipe')
        .output(metaitem('distillation_tower'))
        .matrix('CHC', 'PFP', 'CHC')
        .key('F', ore('frameGtStainlessSteel'))
        .key('C', ore('circuitHv'))
        .key('H', ore('pipeLargeFluidStainlessSteel'))
        .key('P', metaitem('electric.pump.hv'))
        .register()

//Cleanroom
crafting.remove('gregtech:cleanroom')
crafting.shapedBuilder().name('cleanroom')
        .output(metaitem('cleanroom'))
        .matrix('GGG', 'HPH', 'CFC')
        .key('F', item('gregtech:meta_item_1', 128))
        .key('C', ore('circuitMv'))
        .key('H', item('gregtech:meta_rotor', 324))
        .key('P', item('gregtech:mte', 987))
        .key('G', item('gregtech:meta_item_1', 291))
        .register()

// Plascrete Cabal
mods.gregtech.assembler.removeByInput(48, [metaitem('frameSteel'), metaitem('platePlastic') * 6], [fluid('concrete') * 144 * 144])
//New Plascrete
recipemap('assembler').recipeBuilder()
        .fluidInputs(fluid('concrete') * 144)
        .inputs(item('gregtech:meta_plate', 1012) * 6)
        .inputs(item('gregtech:meta_block_frame_20', 4) * 1)
        .outputs(item('gregtech:cleanroom_casing') * 4)
        .duration(40)
        .EUt(128).buildAndRegister();




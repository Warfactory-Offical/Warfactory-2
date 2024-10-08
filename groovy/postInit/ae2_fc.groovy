
// Fluid Discretizer
crafting.remove('ae2fc:fluid_discretizer')
crafting.shapedBuilder().name('fluid_discretizer')
        .output(item('ae2fc:fluid_discretizer'))
        .matrix('PDP', 'ECS', 'PUP')
        .key('P', ore('plateStainlessSteel'))
        .key('D', ore('cableGtDoubleAluminium'))
        .key('E', metaitem('emitter.hv'))
        .key('C', ore('circuitHv'))
        .key('S', metaitem('sensor.hv'))
        .key('U', metaitem('electric.pump.hv'))
        .mirrored()
        .register()

// Fluid Pattern Encoder
mods.jei.ingredient.hide(item('ae2fc:fluid_pattern_encoder'))
crafting.remove('ae2fc:fluid_pattern_encoder')

// Fluid Packet Decoder
crafting.remove('ae2fc:fluid_packet_decoder')
crafting.shapedBuilder().name('fluid_packet_decoder')
        .output(item('ae2fc:fluid_packet_decoder'))
        .matrix('PCP', 'OKU', 'PSP')
        .key('P', ore('plateTungstenSteel'))
        .key('C', ore('cableGtDoubleGold'))
        .key('O', metaitem('conveyor.module.hv'))
        .key('K', ore('circuitEv'))
        .key('U', metaitem('electric.pump.hv'))
        .key('S', metaitem('sensor.hv'))
        .mirrored()
        .register()

// Ingredient Buffer
mods.jei.ingredient.hide(item('ae2fc:ingredient_buffer'))
crafting.remove('ae2fc:ingredient_buffer')

// Large Ingredient Buffer
mods.jei.ingredient.hide(item('ae2fc:large_ingredient_buffer'))
crafting.remove('ae2fc:large_ingredient_buffer')

// Precision Burette
crafting.remove('ae2fc:burette')
crafting.shapedBuilder().name('burette')
        .output(item('ae2fc:burette'))
        .matrix('PRP', 'GCG', 'PPP')
        .key('P', ore('plateSteel'))
        .key('R', metaitem('fluid.regulator.hv'))
        .key('G', item('gregtech:transparent_casing'))
        .key('C', ore('chestWood'))
        .register()

// Dual Interface
crafting.remove('ae2fc:dual_interface')
crafting.shapedBuilder().name('dual_interface')
        .output(item('ae2fc:dual_interface'))
        .matrix('OPO', 'ICF', 'OPO')
        .key('I', item('appliedenergistics2:interface'))
        .key('C', ore('circuitHv'))
        .key('F', item('appliedenergistics2:fluid_interface'))
        .key('P', ore('plateTitanium'))
        .key('O', ore('screwStainlessSteel'))
        .mirrored()
        .register()

// Fluid Level Maintainer
mods.jei.ingredient.hide(item('ae2fc:fluid_level_maintainer'))
crafting.remove('ae2fc:fluid_level_maintainer')

// Fluid Assembler
crafting.remove('ae2fc:fluid_assembler')
crafting.shapedBuilder().name('fluid_assembler')
        .output(item('ae2fc:fluid_assembler'))
        .matrix('PCP', 'EME', 'PRP')
        .key('P', ore('plateSteel'))
        .key('C', item('appliedenergistics2:part', 16))
        .key('E', item('appliedenergistics2:material', 22))
        .key('M', item('appliedenergistics2:molecular_assembler'))
        .key('R', metaitem('fluid.regulator.lv'))
        .register()

// Fluid Pattern Terminal
crafting.remove('ae2fc:part_fluid_pattern_terminal')
crafting.shapedBuilder().name('fluid_pattern_terminal')
        .output(item('ae2fc:part_fluid_pattern_terminal'))
        .matrix('TA', 'BC')
        .key('T', item('appliedenergistics2:part', 340))
        .key('A', metaitem('fluid.regulator.hv'))
        .key('B', metaitem('emitter.hv'))
        .key('C', ore('circuitIv'))
        .register()

// Extended Fluid Pattern Terminal
crafting.remove('ae2fc:part_fluid_pattern_ex_terminal')
crafting.shapedBuilder().name('fluid_pattern_ex_terminal')
        .output(item('ae2fc:part_fluid_pattern_ex_terminal'))
        .matrix('TA', 'BC')
        .key('T', item('appliedenergistics2:part', 341))
        .key('A', metaitem('fluid.regulator.ev'))
        .key('B', metaitem('emitter.ev'))
        .key('C', ore('circuitLuv'))
        .register()

// ME Ultimate Encoder
crafting.remove('ae2fc:ultimate_encoder')
crafting.shapedBuilder().name('ultimate_encoder')
        .output(item('ae2fc:ultimate_encoder'))
        .matrix('PTP', 'SFE', 'PCP')
        .key('P', ore('plateDenseNaquadahAlloy'))
        .key('T', item('ae2fc:part_fluid_pattern_ex_terminal'))
        .key('S', metaitem('sensor.zpm'))
        .key('F', metaitem('field.generator.zpm'))
        .key('E', metaitem('emitter.zpm'))
        .key('C', ore('circuitUv'))
        .mirrored()
        .register()

// Wireless Fluid Pattern Terminal
crafting.remove('ae2fc:wireless_fluid_pattern_terminal')
crafting.shapedBuilder().name('wireless_fluid_pattern_terminal')
        .output(item('ae2fc:wireless_fluid_pattern_terminal'))
        .matrix('TC', 'Kd')
        .key('d', ore('toolScrewdriver')) //TODO native tools
        .key('T', item('appliedenergistics2:wireless_pattern_terminal'))
        .key('C', ore('circuitEv'))
        .key('K', metaitem('fluid.regulator.ev'))
        .register()


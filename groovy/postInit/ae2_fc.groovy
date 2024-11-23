
// Fluid Discretizer
crafting.remove('ae2fc:fluid_discretizer')
crafting.shapedBuilder().name('fluid_discretizer')
        .output(item('ae2fc:fluid_discretizer'))
        .matrix('PDP', 'ECS', 'PUP')
        .key('P', ore('plateAluminium'))
        .key('D', ore('cableGtDoubleCopper'))
        .key('E', metaitem('emitter.mv'))
        .key('C', ore('circuitMv'))
        .key('S', metaitem('sensor.mv'))
        .key('U', metaitem('electric.pump.mv'))
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
        .matrix('ICF')
        .key('I', item('appliedenergistics2:interface'))
        .key('C', ore('circuitMv'))
        .key('F', item('appliedenergistics2:fluid_interface'))
        .mirrored()
        .register()


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
        .key('A', metaitem('fluid.regulator.mv'))
        .key('B', metaitem('emitter.mv'))
        .key('C', ore('circuitMv'))
        .register()

// Extended Fluid Pattern Terminal
crafting.remove('ae2fc:part_fluid_pattern_ex_terminal')
crafting.shapedBuilder().name('fluid_pattern_ex_terminal')
        .output(item('ae2fc:part_fluid_pattern_ex_terminal'))
        .matrix('TA', 'BC')
        .key('T', item('appliedenergistics2:part', 341))
        .key('A', metaitem('fluid.regulator.mv'))
        .key('B', metaitem('emitter.mv'))
        .key('C', ore('circuitMv'))
        .register()

// ME Ultimate Encoder
crafting.remove('ae2fc:ultimate_encoder')
crafting.shapedBuilder().name('ultimate_encoder')
        .output(item('ae2fc:ultimate_encoder'))
        .matrix('PTP', 'SFE', 'PCP')
        .key('P', ore('plateDenseOsmium'))
        .key('T', item('ae2fc:part_fluid_pattern_ex_terminal'))
        .key('S', metaitem('sensor.iv'))
        .key('F', metaitem('field.generator.iv'))
        .key('E', metaitem('emitter.iv'))
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
        .key('C', ore('circuitZpm'))
        .key('K', metaitem('fluid.regulator.iv'))
        .register()


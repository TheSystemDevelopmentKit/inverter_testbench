add wave -position insertpoint  \
sim/:tb_inverter_testbench:A \
sim/:tb_inverter_testbench:initdone \
sim/:tb_inverter_testbench:clock \
sim/:tb_inverter_testbench:Z \

run -all

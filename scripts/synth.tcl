foreach variable {EDA_TOP EDA_SOURCE_MANIFEST EDA_OUTPUT_DIR EDA_FLATTEN EDA_YOSYS} {
    if {![info exists ::env($variable)]} {
        error "Required environment variable is missing: $variable"
    }
}

set top $::env(EDA_TOP)
set manifest $::env(EDA_SOURCE_MANIFEST)
set output_dir $::env(EDA_OUTPUT_DIR)
set yosys_script [file join $output_dir generated.ys]

proc yosys_quote {value} {
    set escaped [string map [list "\\" "\\\\" "\"" "\\\""] $value]
    return "\"$escaped\""
}

set source_file [open $manifest r]
set script_file [open $yosys_script w]
while {[gets $source_file source] >= 0} {
    set source [string trim $source]
    if {$source ne ""} {
        puts $script_file "read_verilog -sv [yosys_quote $source]"
    }
}
close $source_file

puts $script_file "hierarchy -check -top $top"
puts $script_file "proc"
puts $script_file "opt"
puts $script_file "check"

if {$::env(EDA_FLATTEN) eq "1"} {
    puts $script_file "flatten"
}

puts $script_file "techmap"
puts $script_file "opt"
puts $script_file "check"
puts $script_file "write_verilog -noattr netlist.v"
puts $script_file "tee -o stats.json stat -json"
close $script_file

cd $output_dir
if {[catch {exec $::env(EDA_YOSYS) -s $yosys_script 2>@1} output options]} {
    puts $output
    exit 1
}
puts $output

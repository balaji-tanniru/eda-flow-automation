module toggle_counter #(parameter int WIDTH=8)(input logic clk,input logic reset_n,input logic enable,output logic[WIDTH-1:0]count);
 always_ff @(posedge clk or negedge reset_n) begin if(!reset_n) count<='0; else if(enable) count<=count+1'b1; end
endmodule

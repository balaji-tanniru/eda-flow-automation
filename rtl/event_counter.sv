module event_counter #(
    parameter int WIDTH = 16
) (
    input  logic             clk,
    input  logic             reset_n,
    input  logic             enable,
    input  logic             clear,
    output logic [WIDTH-1:0] count,
    output logic             overflow
);

    always_ff @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            count    <= '0;
            overflow <= 1'b0;
        end else if (clear) begin
            count    <= '0;
            overflow <= 1'b0;
        end else if (enable) begin
            count    <= count + 1'b1;
            overflow <= &count;
        end
    end

endmodule


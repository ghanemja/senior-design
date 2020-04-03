// CarWash

module CarWash(
    input [18:0]SW,
    input [3:0]KEY,
    input CLOCK_50,
    output [7:0]LEDG,
    output [18:0]LEDR
);

/* Physical inputs and outputs */
wire clk = CLOCK_50;
// On DE2-115, key up (default state) is 1, key pressed down is 0
wire start = !KEY[0];
wire stop = !KEY[1];
wire rst = KEY[2];


/* Declare outputs */
reg [7:0]step_counter;
reg [7:0]n_step_counter;
reg
	{set_regs}


reg [63:0]rung_count;
always @(posedge clk or negedge rst) begin
    if (rst == 1'b0) begin
        rung_count <= 64'd0;
		{set_resets}
    end
    else begin
        rung_count <= (rung_count + 64'b1) % {rungs_count};

        case (rung_count)
            {set_rungs}
        endcase
    end
end

endmodule
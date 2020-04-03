// ALD_hashigo_ready_01

module ALD_hashigo_ready_01(
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
wire tp1 = !KEY[2];
wire tp2 = !KEY[3];
wire tp3 = !KEY[4];
wire tr = !KEY[5];


/* Declare outputs */
reg [7:0]step_counter;
reg [7:0]n_step_counter;
reg
	SV1,
	SV2,
	SV4,
	VV1,
	VV2,
	heaterson,
	reactorheater,
	SV3,
	heateron,
	heateroff,

	n_SV1,
	n_SV2,
	n_SV4,
	n_VV1,
	n_VV2,
	n_heaterson,
	n_reactorheater,
	n_SV3,
	n_heateron,
	n_heateroff
;


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
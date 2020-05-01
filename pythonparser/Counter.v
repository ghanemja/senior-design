/**
 * The Counter ladder logic module in Verilog.
 * This module counts rising edges on the input signal and flips on the `done' bit
 * once the number of rising edges passes a threshold
 *
 * \param[in] clk: the system clock of the FPGA.
 * \param[in] rst: the system reset signal.
 * \param[in] [31:0] PRE (Preset): the number of counts for this Counter to count up to.
 * \param[in] IN (Counter Enable): On a rising edge, the Counter will increment. A 0 value does not
 *                  reset the Counter. Only the RES command will reset the Counter.
 * \param[in] RES (Counter Reset Command): This is equivalent to a system reset signal and sets all
                    parameters to their default or 0 states.
 * \param[out] DN (Done): 1 if counting is done (ACC >= PRE). This remains high
 *                  after Counter has completed until RES command triggers the Counter to reset.
 * \param[out] CU (Count Up Enable): 1 if Counter Enable is 1. Remains true until Counter Enable
 *                  becomes false or the RES command is triggered. 
 * \param[out] [31:0] ACC (Accumulated): The Counter's count, this is reset to 0 if the RES command 
 *                  is triggered.
 * 
 */

module Counter(
    clk,
    rst,
    PRE,
    IN,
	 RES,
    DN,
	 CU,
	 ACC
);

input clk;
input rst;
input [31:0]PRE;
input IN;
input RES;
output reg DN;
output reg CU;
output reg [31:0]ACC;

// Used to figure out high-low, low-high
// transition of down-sampled clock signal
reg prev_IN;

always @(posedge clk or negedge rst) begin
	if (rst == 1'b0) begin
		prev_IN <= 1'b0;
		ACC <= 32'd0;
		DN <= 1'b0;
		CU <= 1'b0;
	end
	else begin
		prev_IN <= IN;

		if (RES == 1'b1) begin
			ACC <= 32'd0;
			DN <= 1'b0;
			CU <= 1'b0;
		end
		else begin 
			if (IN == 1'b1) begin
				CU <= 1'b1;
				DN <= (ACC >= PRE)? 1'b1 : 1'b0;
				if (prev_IN == 1'b0 && ACC < PRE) begin
					ACC <= ACC + 32'd1;
				end
			end
		end
	end
end

endmodule
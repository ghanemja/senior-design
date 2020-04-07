/**
 * The Timer ladder logic module in Verilog.
 * This module counts in milliseconds and flips on the `done' bit once that
 * much time has elapsed.
 *
 * \param[in] clk: the system clock of the FPGA.
 * \param[in] rst: the reset signal.
 * \param[in] tick: the slowed-down system clock. Frequency must be 1 kHz
 *                 (1 ms per tick).
 * \param[in] [31:0] PRE (Preset): the time for this timer to wait in milliseconds.
 * \param[in] IN (Timer Enable): 1 if this timer should be enabled (i.e. counting), 0
 *                  otherwise. Counter is reset when enabled becomes low.
 * \param[out] DN (Done): 1 if counting is done (ACC >= PRE) and timer is enabled. This remains high
 *                  after timer has completed until Timer is disabled or `rst' is
 *                  triggered.
 * \param[out] TT (Timer Timing): 1 if counting is not done (ACC < PRE) and timer is enabled.
 *                  If timer is done counting (ACC >= PRE) or timer is disabled, TT is 0.
 * \param[out] EN (Enable): 1 if the timer is enabled; Meaning, this bit indicates if the rung
 *                  conditions preceeding the TON are true and the Timer is enabled.
 * \param[out] [31:0] ACC (Accumulated): The Timer's counter, this is reset to 0 if the timer
 *                  is disabled.
 * 
 */

module seniordesigntest(
    clk,
    rst,
    tick,
    PRE,
    IN,
    DN,
	 TT,
	 EN,
	 ACC
);

input clk;
input rst;
input tick;
input [31:0]PRE;
input IN;
output reg DN;
output reg TT;
output reg EN;
output reg [31:0]ACC;

// Used to figure out high-low, low-high
// transition of down-sampled clock signal
reg last_tick;

always @(posedge clk or negedge rst) begin
	if (rst == 1'b0) begin
		last_tick <= 1'b0;
		ACC <= 32'd0;
		DN <= 1'b0;
		TT <= 1'b0;
		EN <= 1'b0;
	end
	else begin
		last_tick <= tick;

		// Timer is note enabled
		if (IN == 1'b0) begin
			ACC <= 32'd0;
			DN <= 1'b0;
			TT <= 1'b0;
			EN <= 1'b0;
		end

		// Timer is enabled
		else 
		begin
			DN <= (ACC >= PRE)? 1'b1 : 1'b0;
			TT <= (ACC < PRE)? 1'b1 : 1'b0;
			EN <= 1'b1;

			// Increment ACC on posedge of down-sampled clock until it reaches PRE
			if (tick != last_tick && tick == 1'b1) begin
				ACC <= (ACC >= PRE)? ACC : ACC + 32'd1;
			end
		end
	end
end

endmodule
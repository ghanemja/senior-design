// andor

module andor(
    input [18:0]SW,
    input [3:0]KEY,
    input CLOCK_50,
    output [7:0]LEDG,
    output [18:0]LEDR
);

/* Physical inputs and outputs */
wire clk = CLOCK_50;
// On DE2-115, key up (default state) is 1, key pressed down is 0
wire mstart = !KEY[0];
wire on_4 = !KEY[1];


/* Declare regs (variables and outputs) */
reg [7:0]step_counter;
reg [7:0]n_step_counter;

reg out_1;
reg out_2;
reg [31:0]cycles.PRE;
reg [31:0]precursor1;
reg [31:0]precursor2;
reg [31:0]precursor3;
reg [31:0]ton2;
reg [31:0]ton3;
reg [31:0]tonp1.PRE;
reg [31:0]tvac1.PRE;
reg [31:0]tvac2;
reg [31:0]tvac3;
reg [31:0]tvacw.PRE;
reg [31:0]twait1.PRE;
reg [31:0]twait2;
reg [31:0]twait3;
reg [31:0]twaitw.PRE;
reg [31:0]twater.PRE;

reg n_out_1;
reg n_out_2;
reg [31:0]n_cycles.PRE;
reg [31:0]n_precursor1;
reg [31:0]n_precursor2;
reg [31:0]n_precursor3;
reg [31:0]n_ton2;
reg [31:0]n_ton3;
reg [31:0]n_tonp1.PRE;
reg [31:0]n_tvac1.PRE;
reg [31:0]n_tvac2;
reg [31:0]n_tvac3;
reg [31:0]n_tvacw.PRE;
reg [31:0]n_twait1.PRE;
reg [31:0]n_twait2;
reg [31:0]n_twait3;
reg [31:0]n_twaitw.PRE;
reg [31:0]n_twater.PRE;

/* Additional modules/functions */
// Make a slowed-down (1kHz) clock
wire tick;
DownClock down(clk, rst, tick);    //########## "rst" not found in inputs, please add a "rst" input variable or rename "rst" in this module header to your reset switch

/* Rung 0 */
wire n_timer_1_done_wire;
Timer t1(clk, rst, tick, 32'd5, main_wash, n_timer_1_done_wire);

wire n_timer_2_done_wire;
Timer t2(clk, rst, tick, 32'd10, main_wash, n_timer_2_done_wire);

/* Rung 3 */
wire n_timer_3_done_wire;
Timer t3(clk, rst, tick, 32'd0, main_wash, n_timer_3_done_wire);




reg [63:0]rung_count;
always @(posedge clk or negedge rst) begin
    if (rst == 1'b0) begin
        rung_count <= 64'd0;
		
		out_1 <= 1'b0
		out_2 <= 1'b0

		cycles.PRE <= 32'd0
		precursor1 <= 32'd0
		precursor2 <= 32'd0
		precursor3 <= 32'd0
		ton2 <= 32'd0
		ton3 <= 32'd0
		tonp1.PRE <= 32'd0
		tvac1.PRE <= 32'd0
		tvac2 <= 32'd0
		tvac3 <= 32'd0
		tvacw.PRE <= 32'd0
		twait1.PRE <= 32'd0
		twait2 <= 32'd0
		twait3 <= 32'd0
		twaitw.PRE <= 32'd0
		twater.PRE <= 32'd0
    end
    else begin
        rung_count <= (rung_count + 64'b1) % 5;

        case (rung_count)
			0: begin
				n_out_1 <= n_on_1 && n_on_2;
			end

			1: begin
				n_out_2 <= (n_on_3 || n_on_4 );
			end

			2: begin
				if ((n_mstart && !n_on_1) == 1'b1)
				begin
					n_tvacw.PRE <= 1'b0;
					n_twaitw.PRE <= 1'b0;
					n_twater.PRE <= 1'b0;
					n_cycles.PRE <= 1'b0;
					n_tvac3 <= 1'b0;
					n_tvac2 <= 1'b0;
					n_tvac1.PRE <= 1'b0;
					n_twait3 <= 1'b0;
					n_twait2 <= 1'b0;
					n_twait1.PRE <= 1'b0;
					n_ton3 <= 1'b0;
					n_ton2 <= 1'b0;
					n_tonp1.PRE <= 1'b0;
					n_precursor3 <= 1'b0;
					n_precursor2 <= 1'b0;
					n_precursor1 <= 1'b0;
				end
			end

			3: begin
			end

			4: begin
				out_1 <= n_out_1;
				out_2 <= n_out_2;

				cycles.PRE <= n_cycles.PRE;
				precursor1 <= n_precursor1;
				precursor2 <= n_precursor2;
				precursor3 <= n_precursor3;
				ton2 <= n_ton2;
				ton3 <= n_ton3;
				tonp1.PRE <= n_tonp1.PRE;
				tvac1.PRE <= n_tvac1.PRE;
				tvac2 <= n_tvac2;
				tvac3 <= n_tvac3;
				tvacw.PRE <= n_tvacw.PRE;
				twait1.PRE <= n_twait1.PRE;
				twait2 <= n_twait2;
				twait3 <= n_twait3;
				twaitw.PRE <= n_twaitw.PRE;
				twater.PRE <= n_twater.PRE;
			end

        endcase
    end
end

endmodule
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
wire on_1 = !KEY[0];
wire on_2 = !KEY[1];
wire on_3 = !KEY[2];
wire on_4 = !KEY[3];


/* Declare outputs */
reg [7:0]step_counter;
reg [7:0]n_step_counter;
reg
	out1,
	out2,

	n_out1,
	n_out2
;


wire tick;
DownClock down(clk, rst, tick);    //########## "rst" not found in inputs, please add or rename rst in this module




reg [63:0]rung_count;
always @(posedge clk or negedge rst) begin
    if (rst == 1'b0) begin
        rung_count <= 64'd0;
		
		cycles.PRE <= 32'd0
		mstart <= 1'b0
		nsection <= 32'd0
		out_1 <= 1'b0
		out_2 <= 1'b0
		precursor1 <= 32'd0
		precursor2 <= 32'd0
		precursor3 <= 32'd0
		reactorheater <= 1'b0
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
		vacpumps <= 1'b0
    end
    else begin
        rung_count <= (rung_count + 64'b1) % 7;

        case (rung_count)
			0: begin
				n_out_2 <= n_on_3 || n_on_2 && ((n_on_1 || n_on_2 )|| n_on_2 );
				n_out_1 <= n_on_3 || n_on_2 && ((n_on_1 || n_on_2 )|| n_on_2 );
			end

			1: begin
				n_mstart <= (n_TP1 && n_TP2 && n_TP3 && n_TR || n_mstart && n_Stop && !n_mstop );
			end

			2: begin
				n_reactorheater <= (n_mstart || n_reactorheater )&& !n_mstop ;
			end

			3: begin
				n_vacpumps <= (n_tpvac.TT || n_mstart && n_vacpumps && !n_pulse_start.EN );
			end

			4: begin
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

			5: begin
				n_nsection <= 32'd1 + nsection;
			end

			6: begin
				out_2 <= n_out_2;
				out_1 <= n_out_1;
				mstart <= n_mstart;
				reactorheater <= n_reactorheater;
				vacpumps <= n_vacpumps;
				tvacw.PRE <= n_tvacw.PRE;
				twaitw.PRE <= n_twaitw.PRE;
				twater.PRE <= n_twater.PRE;
				cycles.PRE <= n_cycles.PRE;
				tvac3 <= n_tvac3;
				tvac2 <= n_tvac2;
				tvac1.PRE <= n_tvac1.PRE;
				twait3 <= n_twait3;
				twait2 <= n_twait2;
				twait1.PRE <= n_twait1.PRE;
				ton3 <= n_ton3;
				ton2 <= n_ton2;
				tonp1.PRE <= n_tonp1.PRE;
				precursor3 <= n_precursor3;
				precursor2 <= n_precursor2;
				precursor1 <= n_precursor1;
				nsection <= n_nsection;
			end

        endcase
    end
end

endmodule
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
wire  stop = !KEY[1];
wire  tp1 = !KEY[2];
wire  tp2 = !KEY[3];
wire  tp3 = !KEY[4];
wire  tr = !KEY[5];


/* Declare regs (variables and outputs) */
reg [7:0]step_counter;
reg [7:0]n_step_counter;

reg SV1;
reg Tok;
reg VV1;
reg VV2;
reg mstart;
reg pulse_start_IN;
reg reactorheater;
reg restart_p_IN;
reg restart_s_IN;
reg startpos;
reg sv1;
reg sv2;
reg sv3;
reg svac1;
reg tonp1_IN;
reg tpstart_IN;
reg tpvac_IN;
reg trestarts_IN;
reg trig11;
reg trig21;
reg trig71;
reg trig81;
reg tvac1_IN;
reg tvacw_IN;
reg twater_IN;
reg vacpumps;
reg [31:0]TBw;
reg [31:0]cycleperspec;
reg [31:0]cycles_PRE;
reg [31:0]precursor1;
reg [31:0]precursor2;
reg [31:0]precursor3;
reg [31:0]ton2;
reg [31:0]ton3;
reg [31:0]tonp1_PRE;
reg [31:0]tvac1_PRE;
reg [31:0]tvac2;
reg [31:0]tvac3;
reg [31:0]tvacw_PRE;
reg [31:0]twait1_PRE;
reg [31:0]twait2;
reg [31:0]twait3;
reg [31:0]twaitw_PRE;
reg [31:0]twater_PRE;

reg n_SV1;
reg n_Tok;
reg n_VV1;
reg n_VV2;
reg n_mstart;
reg n_pulse_start_IN;
reg n_reactorheater;
reg n_restart_p_IN;
reg n_restart_s_IN;
reg n_startpos;
reg n_sv1;
reg n_sv2;
reg n_sv3;
reg n_svac1;
reg n_tonp1_IN;
reg n_tpstart_IN;
reg n_tpvac_IN;
reg n_trestarts_IN;
reg n_trig11;
reg n_trig21;
reg n_trig71;
reg n_trig81;
reg n_tvac1_IN;
reg n_tvacw_IN;
reg n_twater_IN;
reg n_vacpumps;
reg [31:0]n_TBw;
reg [31:0]n_cycleperspec;
reg [31:0]n_cycles_PRE;
reg [31:0]n_precursor1;
reg [31:0]n_precursor2;
reg [31:0]n_precursor3;
reg [31:0]n_ton2;
reg [31:0]n_ton3;
reg [31:0]n_tonp1_PRE;
reg [31:0]n_tvac1_PRE;
reg [31:0]n_tvac2;
reg [31:0]n_tvac3;
reg [31:0]n_tvacw_PRE;
reg [31:0]n_twait1_PRE;
reg [31:0]n_twait2;
reg [31:0]n_twait3;
reg [31:0]n_twaitw_PRE;
reg [31:0]n_twater_PRE;

/* Additional modules/functions */
// Make a slowed-down (1kHz) clock
wire tick;
DownClock down(clk, rst, tick);

/* Rung 1 */
// Timer: tpvac
wire [31:0]tpvac_ACC;
wire tpvac_DN, tpvac_TT, tpvac_EN;
Timer t1(clk, rst, tick, 32'd10, tpvac_IN, tpvac_DN, tpvac_TT, tpvac_EN, tpvac_ACC);

/* Rung 4 */
// Timer: pulse_start
wire [31:0]pulse_start_ACC;
wire pulse_start_DN, pulse_start_TT, pulse_start_EN;
Timer t2(clk, rst, tick, 32'd1001, pulse_start_IN, pulse_start_DN, pulse_start_TT, pulse_start_EN, pulse_start_ACC);

/* Rung 5 */
// Timer: restart_s
wire [31:0]restart_s_ACC;
wire restart_s_DN, restart_s_TT, restart_s_EN;
Timer t3(clk, rst, tick, 32'd5, restart_s_IN, restart_s_DN, restart_s_TT, restart_s_EN, restart_s_ACC);

/* Rung 6 */
// Timer: restart_p
wire [31:0]restart_p_ACC;
wire restart_p_DN, restart_p_TT, restart_p_EN;
Timer t4(clk, rst, tick, 32'd0, restart_p_IN, restart_p_DN, restart_p_TT, restart_p_EN, restart_p_ACC);

/* Rung 9 */
// Timer: tpstart
wire [31:0]tpstart_ACC;
wire tpstart_DN, tpstart_TT, tpstart_EN;
Timer t5(clk, rst, tick, 32'd1000, tpstart_IN, tpstart_DN, tpstart_TT, tpstart_EN, tpstart_ACC);

/* Rung 10 */
// Timer: tonp1
wire [31:0]tonp1_ACC;
wire tonp1_DN, tonp1_TT, tonp1_EN;
Timer t6(clk, rst, tick, 32'd0, tonp1_IN, tonp1_DN, tonp1_TT, tonp1_EN, tonp1_ACC);

/* Rung 12 */
// Timer: tvac1
wire [31:0]tvac1_ACC;
wire tvac1_DN, tvac1_TT, tvac1_EN;
Timer t7(clk, rst, tick, 32'd0, tvac1_IN, tvac1_DN, tvac1_TT, tvac1_EN, tvac1_ACC);

/* Rung 14 */
// Timer: twater
wire [31:0]twater_ACC;
wire twater_DN, twater_TT, twater_EN;
Timer t8(clk, rst, tick, 32'd0, twater_IN, twater_DN, twater_TT, twater_EN, twater_ACC);

/* Rung 16 */
// Timer: tvacw
wire [31:0]tvacw_ACC;
wire tvacw_DN, tvacw_TT, tvacw_EN;
Timer t9(clk, rst, tick, 32'd0, tvacw_IN, tvacw_DN, tvacw_TT, tvacw_EN, tvacw_ACC);

/* Rung 18 */
// Timer: trestarts
wire [31:0]trestarts_ACC;
wire trestarts_DN, trestarts_TT, trestarts_EN;
Timer t10(clk, rst, tick, 32'd0, trestarts_IN, trestarts_DN, trestarts_TT, trestarts_EN, trestarts_ACC);




reg [63:0]rung_count;
always @(posedge clk or negedge rst) begin
    if (rst == 1'b0) begin
        rung_count <= 64'd0;
		
		SV1 <= 1'b0;
		Tok <= 1'b0;
		VV1 <= 1'b0;
		VV2 <= 1'b0;
		mstart <= 1'b0;
		pulse_start_IN <= 1'b0;
		reactorheater <= 1'b0;
		restart_p_IN <= 1'b0;
		restart_s_IN <= 1'b0;
		startpos <= 1'b0;
		sv1 <= 1'b0;
		sv2 <= 1'b0;
		sv3 <= 1'b0;
		svac1 <= 1'b0;
		tonp1_IN <= 1'b0;
		tpstart_IN <= 1'b0;
		tpvac_IN <= 1'b0;
		trestarts_IN <= 1'b0;
		trig11 <= 1'b0;
		trig21 <= 1'b0;
		trig71 <= 1'b0;
		trig81 <= 1'b0;
		tvac1_IN <= 1'b0;
		tvacw_IN <= 1'b0;
		twater_IN <= 1'b0;
		vacpumps <= 1'b0;

		TBw <= 32'd0;
		cycleperspec <= 32'd0;
		cycles_PRE <= 32'd0;
		precursor1 <= 32'd0;
		precursor2 <= 32'd0;
		precursor3 <= 32'd0;
		ton2 <= 32'd0;
		ton3 <= 32'd0;
		tonp1_PRE <= 32'd0;
		tvac1_PRE <= 32'd0;
		tvac2 <= 32'd0;
		tvac3 <= 32'd0;
		tvacw_PRE <= 32'd0;
		twait1_PRE <= 32'd0;
		twait2 <= 32'd0;
		twait3 <= 32'd0;
		twaitw_PRE <= 32'd0;
		twater_PRE <= 32'd0;
    end
    else begin
        rung_count <= (rung_count + 64'b1) % 27;

        case (rung_count)
			0: begin
				n_mstart <= (n_TP1 && n_TP2 && n_TP3 && n_TR || n_mstart && n_Stop && !n_mstop );
			end

			1: begin
				n_tpvac_IN <= n_mstart;
			end

			2: begin
				n_reactorheater <= (n_mstart || n_reactorheater )&& !n_mstop;
			end

			3: begin
				n_vacpumps <= n_mstart && n_vacpumps;
			end

			4: begin
				n_Tok <= (n_TR || n_Tok );
				n_pulse_start_IN <= (n_TR || n_Tok );
			end

			5: begin
				n_restart_s_IN <= n_s_dones;
			end

			6: begin
				n_restart_p_IN <= n_sdone_p;
			end

			7: begin
				if ((n_mstart && (|| (|| ))&& () == 1'b1)
				begin
					n_cycleperspec <= 32'd0;
					n_TBw <= 32'd0;
				end
			end

			8: begin
				if ((n_mstart) == 1'b1)
				begin
					n_tvacw_PRE <= 32'd0;
					n_twaitw_PRE <= 32'd0;
					n_twater_PRE <= 32'd0;
					n_cycles_PRE <= 32'd0;
					n_tvac3 <= 32'd0;
					n_tvac2 <= 32'd0;
					n_tvac1_PRE <= 32'd0;
					n_twait3 <= 32'd0;
					n_twait2 <= 32'd0;
					n_twait1_PRE <= 32'd0;
					n_ton3 <= 32'd0;
					n_ton2 <= 32'd0;
					n_tonp1_PRE <= 32'd0;
					n_precursor3 <= 32'd0;
					n_precursor2 <= 32'd0;
					n_precursor1 <= 32'd0;
				end
			end

			9: begin
				n_startpos <= n_start_serial;
				n_tpstart_IN <= n_start_serial;
			end

			10: begin
				n_tonp1_IN <= !n_done1;
			end

			11: begin
				n_trig11 <= !n_startpos && n_trig11 && !n_trig81;
			end

			12: begin
				n_tvac1_IN <= n_trig11 &&;
			end

			13: begin
				n_trig21 <= n_trig21 && !n_startpos && !n_trig81;
			end

			14: begin
				n_twater_IN <= n_trig21;
			end

			15: begin
				n_trig71 <= n_trig71 && !n_startpos;
			end

			16: begin
				n_tvacw_IN <= n_trig71 &&;
			end

			17: begin
				n_trig81 <= n_trig81 && !n_startpos;
			end

			18: begin
				n_trestarts_IN <= n_trig81;
			end

			19: begin
				n_sv1 <= n_sv11;
			end

			20: begin
				n_sv2 <= n_sv21;
			end

			21: begin
				n_sv3 <= n_sv31;
			end

			22: begin
				n_svac1 <= n_svac11;
			end

			23: begin
				n_SV1 <= n_sv1;
			end

			24: begin
				n_VV1 <= (n_vacpumps || n_svac1 );
			end

			25: begin
				n_VV2 <= n_vacpumps;
			end

			26: begin
				SV1 <= n_SV1;
				Tok <= n_Tok;
				VV1 <= n_VV1;
				VV2 <= n_VV2;
				mstart <= n_mstart;
				pulse_start_IN <= n_pulse_start_IN;
				reactorheater <= n_reactorheater;
				restart_p_IN <= n_restart_p_IN;
				restart_s_IN <= n_restart_s_IN;
				startpos <= n_startpos;
				sv1 <= n_sv1;
				sv2 <= n_sv2;
				sv3 <= n_sv3;
				svac1 <= n_svac1;
				tonp1_IN <= n_tonp1_IN;
				tpstart_IN <= n_tpstart_IN;
				tpvac_IN <= n_tpvac_IN;
				trestarts_IN <= n_trestarts_IN;
				trig11 <= n_trig11;
				trig21 <= n_trig21;
				trig71 <= n_trig71;
				trig81 <= n_trig81;
				tvac1_IN <= n_tvac1_IN;
				tvacw_IN <= n_tvacw_IN;
				twater_IN <= n_twater_IN;
				vacpumps <= n_vacpumps;

				TBw <= n_TBw;
				cycleperspec <= n_cycleperspec;
				cycles_PRE <= n_cycles_PRE;
				precursor1 <= n_precursor1;
				precursor2 <= n_precursor2;
				precursor3 <= n_precursor3;
				ton2 <= n_ton2;
				ton3 <= n_ton3;
				tonp1_PRE <= n_tonp1_PRE;
				tvac1_PRE <= n_tvac1_PRE;
				tvac2 <= n_tvac2;
				tvac3 <= n_tvac3;
				tvacw_PRE <= n_tvacw_PRE;
				twait1_PRE <= n_twait1_PRE;
				twait2 <= n_twait2;
				twait3 <= n_twait3;
				twaitw_PRE <= n_twaitw_PRE;
				twater_PRE <= n_twater_PRE;
			end

        endcase
    end
end

endmodule
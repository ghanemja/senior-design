// ALD_miami

module ALD_miami(
    SW,
    KEY,
    CLOCK_50,
    LEDG,
    LEDR
);

input [18:0]SW;
input [3:0]KEY;
input CLOCK_50;
output [7:0]LEDG;
output [18:0]LEDR;

/* Physical inputs and outputs */
wire clk = CLOCK_50;
wire rst = SW[0];
wire n_Start = SW[1];
wire n_Stop = SW[2];
wire n_TP1 = SW[3];
wire n_TR = SW[4];
wire n_Pressure_Switch = SW[5];
wire n_Atmosphere = SW[6];

assign LEDG[0] = SV1;
assign LEDG[1] = SV4;
assign LEDG[2] = VV1;
assign LEDG[3] = VV2;
assign LEDG[4] = reactorheater;
assign LEDG[5] = mfcwater;


/* Declare regs (variables and outputs) */
reg [7:0]step_counter;
reg [7:0]n_step_counter;

reg MFC;
reg SV1;
reg SV4;
reg Tok;
reg VV1;
reg VV2;
reg cycles_IN;
reg cycles_RES;
reg delay_start_IN;
reg done;
reg done1;
reg mfcwater;
reg mstart;
reg mstop;
reg prev_start_serial;
reg prev_tvac1_DN;
reg prev_tvacw_DN;
reg prev_twater_DN;
reg pulse_start_IN;
reg reactorheater;
reg start_section_IN;
reg start_serial;
reg startpos;
reg sv11;
reg svac1;
reg svac2;
reg sw;
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
reg twait1_IN;
reg twaitw_IN;
reg twater_IN;
reg vacpumps;
reg [31:0]cycles_PRE = 32'd9;
reg [31:0]delay_start_PRE = 32'd1000;
reg [31:0]precursor1;
reg [31:0]pulse_start_PRE = 32'd1001;
reg [31:0]start_section_PRE = 32'd5000;
reg [31:0]tonp1_PRE = 32'd2000;
reg [31:0]tpstart_PRE = 32'd1000;
reg [31:0]tpvac_PRE = 32'd20;
reg [31:0]trestarts_PRE = 32'd0;
reg [31:0]tvac1_PRE = 32'd4000;
reg [31:0]tvacw_PRE = 32'd8000;
reg [31:0]twait1_PRE = 32'd3000;
reg [31:0]twaitw_PRE = 32'd7000;
reg [31:0]twater_PRE = 32'd6000;

reg n_MFC;
reg n_SV1;
reg n_SV4;
reg n_Tok;
reg n_VV1;
reg n_VV2;
reg n_cycles_IN;
reg n_cycles_RES;
reg n_delay_start_IN;
reg n_done;
reg n_done1;
reg n_mfcwater;
reg n_mstart;
reg n_mstop;
reg n_pulse_start_IN;
reg n_reactorheater;
reg n_start_section_IN;
reg n_start_serial;
reg n_startpos;
reg n_sv11;
reg n_svac1;
reg n_svac2;
reg n_sw;
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
reg n_twait1_IN;
reg n_twaitw_IN;
reg n_twater_IN;
reg n_vacpumps;
reg [31:0]n_cycles_PRE = 32'd9;
reg [31:0]n_delay_start_PRE = 32'd1000;
reg [31:0]n_precursor1;
reg [31:0]n_pulse_start_PRE = 32'd1001;
reg [31:0]n_start_section_PRE = 32'd5000;
reg [31:0]n_tonp1_PRE = 32'd2000;
reg [31:0]n_tpstart_PRE = 32'd1000;
reg [31:0]n_tpvac_PRE = 32'd20;
reg [31:0]n_trestarts_PRE = 32'd0;
reg [31:0]n_tvac1_PRE = 32'd4000;
reg [31:0]n_tvacw_PRE = 32'd8000;
reg [31:0]n_twait1_PRE = 32'd3000;
reg [31:0]n_twaitw_PRE = 32'd7000;
reg [31:0]n_twater_PRE = 32'd6000;

/* Additional modules/functions */
// Make a slowed-down (1kHz) clock
wire tick;
DownClock down(clk, rst, tick);

/* Rung 2 */
// Timer: tpvac
wire [31:0]n_tpvac_ACC;
wire n_tpvac_DN, n_tpvac_TT, n_tpvac_EN;
Timer t1(clk, rst, tick, n_tpvac_PRE, n_tpvac_IN, n_tpvac_DN, n_tpvac_TT, n_tpvac_EN, n_tpvac_ACC);

/* Rung 6 */
// Timer: pulse_start
wire [31:0]n_pulse_start_ACC;
wire n_pulse_start_DN, n_pulse_start_TT, n_pulse_start_EN;
Timer t2(clk, rst, tick, n_pulse_start_PRE, n_pulse_start_IN, n_pulse_start_DN, n_pulse_start_TT, n_pulse_start_EN, n_pulse_start_ACC);

/* Rung 7 */
// Timer: start_section
wire [31:0]n_start_section_ACC;
wire n_start_section_DN, n_start_section_TT, n_start_section_EN;
Timer t3(clk, rst, tick, n_start_section_PRE, n_start_section_IN, n_start_section_DN, n_start_section_TT, n_start_section_EN, n_start_section_ACC);

/* Rung 8 */
// Timer: delay_start
wire [31:0]n_delay_start_ACC;
wire n_delay_start_DN, n_delay_start_TT, n_delay_start_EN;
Timer t4(clk, rst, tick, n_delay_start_PRE, n_delay_start_IN, n_delay_start_DN, n_delay_start_TT, n_delay_start_EN, n_delay_start_ACC);

/* Rung 11 */
// Timer: tpstart
wire [31:0]n_tpstart_ACC;
wire n_tpstart_DN, n_tpstart_TT, n_tpstart_EN;
Timer t5(clk, rst, tick, n_tpstart_PRE, n_tpstart_IN, n_tpstart_DN, n_tpstart_TT, n_tpstart_EN, n_tpstart_ACC);

/* Rung 13 */
// Timer: tonp1
wire [31:0]n_tonp1_ACC;
wire n_tonp1_DN, n_tonp1_TT, n_tonp1_EN;
Timer t6(clk, rst, tick, n_tonp1_PRE, n_tonp1_IN, n_tonp1_DN, n_tonp1_TT, n_tonp1_EN, n_tonp1_ACC);

/* Rung 16 */
// Timer: twait1
wire [31:0]n_twait1_ACC;
wire n_twait1_DN, n_twait1_TT, n_twait1_EN;
Timer t7(clk, rst, tick, n_twait1_PRE, n_twait1_IN, n_twait1_DN, n_twait1_TT, n_twait1_EN, n_twait1_ACC);

/* Rung 17 */
// Timer: tvac1
wire [31:0]n_tvac1_ACC;
wire n_tvac1_DN, n_tvac1_TT, n_tvac1_EN;
Timer t8(clk, rst, tick, n_tvac1_PRE, n_tvac1_IN, n_tvac1_DN, n_tvac1_TT, n_tvac1_EN, n_tvac1_ACC);

/* Rung 20 */
// Timer: twater
wire [31:0]n_twater_ACC;
wire n_twater_DN, n_twater_TT, n_twater_EN;
Timer t9(clk, rst, tick, n_twater_PRE, n_twater_IN, n_twater_DN, n_twater_TT, n_twater_EN, n_twater_ACC);

/* Rung 23 */
// Timer: twaitw
wire [31:0]n_twaitw_ACC;
wire n_twaitw_DN, n_twaitw_TT, n_twaitw_EN;
Timer t10(clk, rst, tick, n_twaitw_PRE, n_twaitw_IN, n_twaitw_DN, n_twaitw_TT, n_twaitw_EN, n_twaitw_ACC);

/* Rung 24 */
// Timer: tvacw
wire [31:0]n_tvacw_ACC;
wire n_tvacw_DN, n_tvacw_TT, n_tvacw_EN;
Timer t11(clk, rst, tick, n_tvacw_PRE, n_tvacw_IN, n_tvacw_DN, n_tvacw_TT, n_tvacw_EN, n_tvacw_ACC);

/* Rung 27 */
// Timer: trestarts
wire [31:0]n_trestarts_ACC;
wire n_trestarts_DN, n_trestarts_TT, n_trestarts_EN;
Timer t12(clk, rst, tick, n_trestarts_PRE, n_trestarts_IN, n_trestarts_DN, n_trestarts_TT, n_trestarts_EN, n_trestarts_ACC);

/* Rung 28 */
// Counter: cycles
wire [31:0]n_cycles_ACC;
wire n_cycles_DN, n_cycles_CU;
Counter c1(clk, rst, n_cycles_PRE, n_cycles_IN, n_cycles_RES, n_cycles_DN, n_cycles_CU, n_cycles_ACC);




reg [63:0]rung_count;
always @(posedge clk or negedge rst) begin
    if (rst == 1'b0) begin
        rung_count <= 64'd0;
		
		MFC <= 1'b0;
		SV1 <= 1'b0;
		SV4 <= 1'b0;
		Tok <= 1'b0;
		VV1 <= 1'b0;
		VV2 <= 1'b0;
		cycles_IN <= 1'b0;
		cycles_RES <= 1'b0;
		delay_start_IN <= 1'b0;
		done <= 1'b0;
		done1 <= 1'b0;
		mfcwater <= 1'b0;
		mstart <= 1'b0;
		mstop <= 1'b0;
		prev_start_serial <= 1'b0;
		prev_tvac1_DN <= 1'b0;
		prev_tvacw_DN <= 1'b0;
		prev_twater_DN <= 1'b0;
		pulse_start_IN <= 1'b0;
		reactorheater <= 1'b0;
		start_section_IN <= 1'b0;
		start_serial <= 1'b0;
		startpos <= 1'b0;
		sv11 <= 1'b0;
		svac1 <= 1'b0;
		svac2 <= 1'b0;
		sw <= 1'b0;
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
		twait1_IN <= 1'b0;
		twaitw_IN <= 1'b0;
		twater_IN <= 1'b0;
		vacpumps <= 1'b0;
		cycles_PRE <= 32'd9;
		delay_start_PRE <= 32'd1000;
		precursor1 <= 32'd0;
		pulse_start_PRE <= 32'd1001;
		start_section_PRE <= 32'd5000;
		tonp1_PRE <= 32'd2000;
		tpstart_PRE <= 32'd1000;
		tpvac_PRE <= 32'd20;
		trestarts_PRE <= 32'd0;
		tvac1_PRE <= 32'd4000;
		tvacw_PRE <= 32'd8000;
		twait1_PRE <= 32'd3000;
		twaitw_PRE <= 32'd7000;
		twater_PRE <= 32'd6000;

		n_MFC <= 1'b0;
		n_SV1 <= 1'b0;
		n_SV4 <= 1'b0;
		n_Tok <= 1'b0;
		n_VV1 <= 1'b0;
		n_VV2 <= 1'b0;
		n_cycles_IN <= 1'b0;
		n_cycles_RES <= 1'b0;
		n_delay_start_IN <= 1'b0;
		n_done <= 1'b0;
		n_done1 <= 1'b0;
		n_mfcwater <= 1'b0;
		n_mstart <= 1'b0;
		n_mstop <= 1'b0;
		n_pulse_start_IN <= 1'b0;
		n_reactorheater <= 1'b0;
		n_start_section_IN <= 1'b0;
		n_start_serial <= 1'b0;
		n_startpos <= 1'b0;
		n_sv11 <= 1'b0;
		n_svac1 <= 1'b0;
		n_svac2 <= 1'b0;
		n_sw <= 1'b0;
		n_tonp1_IN <= 1'b0;
		n_tpstart_IN <= 1'b0;
		n_tpvac_IN <= 1'b0;
		n_trestarts_IN <= 1'b0;
		n_trig11 <= 1'b0;
		n_trig21 <= 1'b0;
		n_trig71 <= 1'b0;
		n_trig81 <= 1'b0;
		n_tvac1_IN <= 1'b0;
		n_tvacw_IN <= 1'b0;
		n_twait1_IN <= 1'b0;
		n_twaitw_IN <= 1'b0;
		n_twater_IN <= 1'b0;
		n_vacpumps <= 1'b0;
		n_cycles_PRE <= 32'd9;
		n_delay_start_PRE <= 32'd1000;
		n_precursor1 <= 32'd0;
		n_pulse_start_PRE <= 32'd1001;
		n_start_section_PRE <= 32'd5000;
		n_tonp1_PRE <= 32'd2000;
		n_tpstart_PRE <= 32'd1000;
		n_tpvac_PRE <= 32'd20;
		n_trestarts_PRE <= 32'd0;
		n_tvac1_PRE <= 32'd4000;
		n_tvacw_PRE <= 32'd8000;
		n_twait1_PRE <= 32'd3000;
		n_twaitw_PRE <= 32'd7000;
		n_twater_PRE <= 32'd6000;
    end
    else begin
        rung_count <= (rung_count + 64'b1) % 37;

        case (rung_count)
			0: begin
				n_mstop <= (!n_Stop || n_cycles_DN );
			end

			1: begin
				n_mstart <= (n_Start && n_TP1 || n_mstart && n_Stop && !n_mstop );
			end

			2: begin
				n_tpvac_IN <= n_mstart;
			end

			3: begin
				n_reactorheater <= (n_mstart || n_reactorheater )&& !n_mstop;
			end

			4: begin
				n_vacpumps <= (n_tpvac_TT || n_mstart && n_vacpumps && !n_pulse_start_EN );
			end

			5: begin
				n_MFC <= n_mstart && (n_Pressure_Switch || !n_Atmosphere && n_MFC );
			end

			6: begin
				n_Tok <= (n_mstart && n_TR || n_mstart && n_Tok );
				n_pulse_start_IN <= (n_mstart && n_TR || n_mstart && n_Tok );
			end

			7: begin
				n_start_section_IN <= n_pulse_start_TT;
			end

			8: begin
				n_delay_start_IN <= n_start_section_TT;
			end

			9: begin
				if ((n_mstart) == 1'b1)
				begin
					n_tvacw_PRE <= 32'd8000;
					n_twaitw_PRE <= 32'd7000;
					n_twater_PRE <= 32'd6000;
					n_cycles_PRE <= 32'd9;
					n_tvac1_PRE <= 32'd4000;
					n_twait1_PRE <= 32'd3000;
					n_tonp1_PRE <= 32'd2000;
					n_precursor1 <= 32'd1000;
				end
			end

			10: begin
				n_start_serial <= n_delay_start_EN;
			end

			11: begin
				n_tpstart_IN <= n_start_serial;
			end

			12: begin
				n_startpos <= n_start_serial && (n_start_serial && !prev_start_serial);
			end

			13: begin
				n_tonp1_IN <= (n_precursor1 >= 32'd2) && (n_trestarts_TT && !n_done1 || n_tpstart_EN || !n_tonp1_DN && n_tonp1_EN );
			end

			14: begin
				n_sv11 <= n_tonp1_TT;
			end

			15: begin
				n_trig11 <= (n_tonp1_DN || !n_startpos && n_trig11 && !n_trig81 );
			end

			16: begin
				n_twait1_IN <= n_trig11;
			end

			17: begin
				n_tvac1_IN <= n_twait1_DN;
			end

			18: begin
				n_svac1 <= n_tvac1_TT;
			end

			19: begin
				n_trig21 <= (n_tvac1_DN && (n_tvac1_DN && !prev_tvac1_DN) || n_trig21 && !n_startpos && !n_trig81 );
			end

			20: begin
				n_twater_IN <= n_trig21;
			end

			21: begin
				n_sw <= n_twater_TT;
			end

			22: begin
				n_trig71 <= (n_twater_DN && (n_twater_DN && !prev_twater_DN) || n_trig71 && !n_startpos && !n_trestarts_TT );
			end

			23: begin
				n_twaitw_IN <= n_trig71;
			end

			24: begin
				n_tvacw_IN <= n_twaitw_DN;
			end

			25: begin
				n_svac2 <= n_tvacw_TT;
			end

			26: begin
				n_trig81 <= (n_tvacw_DN && (n_tvacw_DN && !prev_tvacw_DN) || n_trig81 && !n_startpos && !n_trestarts_TT );
			end

			27: begin
				n_trestarts_IN <= n_trig81;
			end

			28: begin
				n_cycles_IN <= n_trestarts_TT;
			end

			29: begin
				n_cycles_RES <= n_startpos;
			end

			30: begin
				n_done1 <= n_cycles_DN;
				n_done <= n_cycles_DN;
			end

			31: begin
				n_SV1 <= n_sv11;
			end

			32: begin
				n_SV4 <= n_sw;
			end

			33: begin
				n_VV1 <= (n_vacpumps || n_svac1 );
			end

			34: begin
				n_VV2 <= (n_vacpumps || n_svac2 );
			end

			35: begin
				n_mfcwater <= n_MFC;
			end

			36: begin
				MFC <= n_MFC;
				SV1 <= n_SV1;
				SV4 <= n_SV4;
				Tok <= n_Tok;
				VV1 <= n_VV1;
				VV2 <= n_VV2;
				cycles_IN <= n_cycles_IN;
				cycles_RES <= n_cycles_RES;
				delay_start_IN <= n_delay_start_IN;
				done <= n_done;
				done1 <= n_done1;
				mfcwater <= n_mfcwater;
				mstart <= n_mstart;
				mstop <= n_mstop;
				pulse_start_IN <= n_pulse_start_IN;
				reactorheater <= n_reactorheater;
				start_section_IN <= n_start_section_IN;
				start_serial <= n_start_serial;
				startpos <= n_startpos;
				sv11 <= n_sv11;
				svac1 <= n_svac1;
				svac2 <= n_svac2;
				sw <= n_sw;
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
				twait1_IN <= n_twait1_IN;
				twaitw_IN <= n_twaitw_IN;
				twater_IN <= n_twater_IN;
				vacpumps <= n_vacpumps;

				cycles_PRE <= n_cycles_PRE;
				delay_start_PRE <= n_delay_start_PRE;
				precursor1 <= n_precursor1;
				pulse_start_PRE <= n_pulse_start_PRE;
				start_section_PRE <= n_start_section_PRE;
				tonp1_PRE <= n_tonp1_PRE;
				tpstart_PRE <= n_tpstart_PRE;
				tpvac_PRE <= n_tpvac_PRE;
				trestarts_PRE <= n_trestarts_PRE;
				tvac1_PRE <= n_tvac1_PRE;
				tvacw_PRE <= n_tvacw_PRE;
				twait1_PRE <= n_twait1_PRE;
				twaitw_PRE <= n_twaitw_PRE;
				twater_PRE <= n_twater_PRE;

				prev_start_serial <= n_start_serial;
				prev_tvac1_DN <= n_tvac1_DN;
				prev_tvacw_DN <= n_tvacw_DN;
				prev_twater_DN <= n_twater_DN;
			end

        endcase
    end
end

endmodule
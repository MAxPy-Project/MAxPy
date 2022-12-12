module adder4(A, B, SUM); 

parameter BITWIDTH = 4;
parameter K = [[PARAM_K]];

input  [3:0] A; 
input  [3:0] B; 
output [3:0] SUM;
[[PARAM_ADDER01]] #(BITWIDTH, K) adder1(A, B, SUM);
endmodule

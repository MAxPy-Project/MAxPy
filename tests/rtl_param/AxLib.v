module copyA #(
  parameter BIT_WIDTH=8,
  parameter K=5 
)(

  input   signed [BIT_WIDTH-1:0] A,B, 
  output  signed [BIT_WIDTH:0] OUT
);
  generate
    if (K == 0) begin
      assign OUT = A + B;
    end else begin
      assign OUT[BIT_WIDTH:K] = A[BIT_WIDTH-1:K] + B[BIT_WIDTH-1:K];
      assign OUT[K-1:0] = A[K-1:0];    
    end
  endgenerate
endmodule 

module copyB #(
  parameter BIT_WIDTH=8,
  parameter K=5 
)(

  input   signed [BIT_WIDTH-1:0] A,B, 
  output  signed [BIT_WIDTH:0] OUT
);
  generate
    if (K == 0) begin
      assign OUT = A + B;
    end else begin
      assign OUT[BIT_WIDTH:K] = A[BIT_WIDTH-1:K] + B[BIT_WIDTH-1:K];
      assign OUT[K-1:0] = B[K-1:0];    
    end
  endgenerate
endmodule 

module loa #(
    parameter BIT_WIDTH=8,
    parameter K=5 
    )(
    
  input   signed [BIT_WIDTH-1:0] A,B, 
    output  signed [BIT_WIDTH:0] OUT
);
  generate
    if (K == 0) begin
      assign OUT = A + B;
    end else begin
      assign OUT[BIT_WIDTH:K] = A[BIT_WIDTH-1:K] + B[BIT_WIDTH-1:K];
      assign OUT[K-1:0] = A[K-1:0] | B[K-1:0];    
    end
  endgenerate
endmodule 

module trunc0 #(
  parameter BIT_WIDTH=8,
  parameter K=5 
)(    
  input   signed [BIT_WIDTH-1:0] A,B, 
  output  signed [BIT_WIDTH:0] OUT
);
  generate
    if (K == 0) begin
      assign OUT = A + B;
    end else begin
      assign OUT[BIT_WIDTH:K] = A[BIT_WIDTH-1:K] + B[BIT_WIDTH-1:K];
      assign OUT[K-1:0] = {K{1'b0}};
    end
  endgenerate
endmodule // trunc0


module trunc1 #(
    parameter BIT_WIDTH=8,
    parameter K=5 
)(
    input   signed [BIT_WIDTH-1:0] A,B, 
    output  signed [BIT_WIDTH:0] OUT
);
  generate
    if (K == 0) begin
      assign OUT = A + B;
    end else 
    begin
      assign OUT[BIT_WIDTH:K] = A[BIT_WIDTH-1:K] + B[BIT_WIDTH-1:K];
      assign OUT[K-1:0] = {K{1'b1}};    
    end
  endgenerate
endmodule // trunc1

module eta1 #(
  parameter BIT_WIDTH=8,
  parameter K=5
)(
  input   signed [BIT_WIDTH-1:0] A,B, 
  output  signed [BIT_WIDTH:0] OUT
);
  wire [K-1:0] P, G, SET_CMD;
  
  genvar i;
  generate
    if (K == 0) begin
      assign OUT = A + B;
    end 
    else begin
      assign OUT[BIT_WIDTH:K] = A[BIT_WIDTH-1:K] + B[BIT_WIDTH-1:K];

      for (i = 0; i < K; i = i + 1)begin
        assign G[i] = A[i] & B[i];
        assign P[i] = A[i] ^ B[i];
      end
      
      assign SET_CMD[K-1] = P[K-1];
      
      for (i = 0; i <= K-2; i = i + 1)begin
        assign SET_CMD[i] = SET_CMD[i+1] | G[i]; 
      end

      for (i = 0; i <= K-1; i = i + 1)begin
        assign OUT[i] = SET_CMD[i] | P[i];
      end
      
    end
  endgenerate
endmodule // eta1

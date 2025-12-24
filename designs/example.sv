module example(input clk, input rst, output reg [7:0] count);
  always @(posedge clk or posedge rst)
    if (rst) count <= 0;
    else count <= count + 1;
endmodule

#ifdef GL_ES
precision mediump float;
#endif

uniform float u_time;
uniform vec2 u_resolution;

// Plot a line on Y using a value between 0.0-1.0
float plot(vec2 st, float pct){
  return  smoothstep( pct-0.02, pct, st.y) -
          smoothstep( pct, pct+0.02, st.y);
}


void main(){
	vec2 st = gl_FragCoord.xy / u_resolution;

	float y = st.x;

	vec3 color = vec3(y, y, y);

	float ptc = plot(st, y);
	color = (1.0 - ptc) * color + ptc * vec3(0.0, 1.0, 0.0);

	gl_FragColor = vec4(color, 1.0);
}

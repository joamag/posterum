import {
    check
} from "k6";
import http from "k6/http";

export default function() {
    const res = http.get("https://posterum.bemisc.com/v1/addresses/validate?key=${YOU_API_KEY}&email=joao@amplemarket.com");
    check(res, {
        "is status 200": (r) => r.status === 200,
    });
}

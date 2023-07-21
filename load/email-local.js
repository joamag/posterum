import {
    check
} from "k6";
import http from "k6/http";

export default function() {
    const res = http.get("http://localhost:8080/v1/addresses/validate?email=joao@amplemarket.com");
    check(res, {
        "is status 200": (r) => r.status === 200,
    });
}

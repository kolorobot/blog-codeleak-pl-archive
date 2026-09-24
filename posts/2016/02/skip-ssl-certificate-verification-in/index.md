---
title: "Skip SSL certificate verification in Spring Rest Template"
date: 2016-02-12T00:54:00.001+01:00
updated: 2016-02-12T00:54:16.717+01:00
author: "Rafał Borowiec"
tags: ["spring"]
original_url: https://blog.codeleak.pl/2016/02/skip-ssl-certificate-verification-in.html
---

# Skip SSL certificate verification in Spring Rest Template

How to skip SSL certificate verification while using Spring Rest Template? Configure Rest Template so it uses Http Client to create requests.

Note: If you are familiar with `sun.security.provider.certpath.SunCertPathBuilderException: unable to find valid certification path to requested target` the below should help you.

# Http Client

Firstly, import `HttpClient` (>4.4), to your project

```
compile('org.apache.httpcomponents:httpclient:4.5.1')
```

# Configure RestTemplate

Configure `SSLContext` using Http Client’s `SSLContexts` factory methods:

```java
TrustStrategy acceptingTrustStrategy = (X509Certificate[] chain, String authType) -> true;

SSLContext sslContext = org.apache.http.ssl.SSLContexts.custom()
        .loadTrustMaterial(null, acceptingTrustStrategy)
        .build();

SSLConnectionSocketFactory csf = new SSLConnectionSocketFactory(sslContext);

CloseableHttpClient httpClient = HttpClients.custom()
        .setSSLSocketFactory(csf)
        .build();

HttpComponentsClientHttpRequestFactory requestFactory =
        new HttpComponentsClientHttpRequestFactory();

requestFactory.setHttpClient(httpClient);

RestTemplate restTemplate = new RestTemplate(requestFactory);
```

`org.apache.http.ssl.TrustStrategy` is used to override standard certificate verification process. In the above example - it always returns `true`, so the certificate can be trusted without further verification.

# The Test

```java
@Test
public void opensSSLPage() throws Exception {
    String uri = "https://some-secured-page.com";
    ResponseEntity<String> entity = restTemplate.getForEntity(uri, String.class);
    assertThat(entity.getStatusCode().is2xxSuccessful()).isTrue();
}
```

# Final Word

The above code helps in certain situations (e.g. testing against servers with self-signed certificates), but it should not be used in production - unless you are 100% sure what you are doing.

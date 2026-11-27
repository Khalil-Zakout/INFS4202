package com.halcyon.uniplace.qa;

import com.github.tomakehurst.wiremock.junit5.WireMockRuntimeInfo;
import com.github.tomakehurst.wiremock.junit5.WireMockTest;
import com.halcyon.uniplace.engine.EngineClient;
import com.halcyon.uniplace.engine.EngineDtos.EligibilityRequest;
import com.halcyon.uniplace.engine.EngineDtos.EligibilityResult;
import com.halcyon.uniplace.engine.EngineDtos.MatchRequest;
import com.halcyon.uniplace.engine.EngineDtos.MatchResult;
import com.halcyon.uniplace.engine.EngineUnavailableException;
import com.halcyon.uniplace.service.SettingsService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.web.client.RestClient;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

import static com.github.tomakehurst.wiremock.client.WireMock.aResponse;
import static com.github.tomakehurst.wiremock.client.WireMock.post;
import static com.github.tomakehurst.wiremock.client.WireMock.stubFor;
import static com.github.tomakehurst.wiremock.client.WireMock.urlEqualTo;
import static org.junit.jupiter.api.Assertions.fail;

/**
 * REL-01: if the Engine is unreachable or returns an error, the Portal refuses the operation with a clear
 * message; it never treats a student as eligible or a result as computed when the Engine could not answer.
 * The Engine is simulated with WireMock answering 503. A FAILING test is the evidence for issue D51.
 */
@WireMockTest
class EngineOutageTest {

    EngineClient client;

    @BeforeEach
    void setUp(WireMockRuntimeInfo wm) {
        SettingsService settings = Mockito.mock(SettingsService.class);
        Mockito.when(settings.engineBaseUrl()).thenReturn("http://127.0.0.1:" + wm.getHttpPort() + "/api/v1");
        client = new EngineClient(RestClient.builder(), settings);
    }

    /** REL-01: an Engine error must not turn into "eligible". Issue: D51. */
    @Test
    void engineErrorIsNeverTreatedAsEligible() {
        stubFor(post(urlEqualTo("/api/v1/eligibility")).willReturn(aResponse().withStatus(503)));
        EligibilityRequest r = new EligibilityRequest();
        r.gpa = new BigDecimal("1.20");          // clearly NOT eligible: below the minimum GPA
        r.creditsCompleted = 10;
        r.standing = "PROBATION";
        r.minGpa = new BigDecimal("2.00");
        r.minCredits = 45;
        r.asOf = LocalDate.of(2026, 11, 27);
        try {
            EligibilityResult result = client.checkEligibility(r);
            if (result.eligible()) {
                fail("REL-01: the Engine answered 503 but the Portal reports the student as eligible");
            }
        } catch (EngineUnavailableException expected) {
            // refusing the operation is the specified behaviour
        }
    }

    /** REL-01: an Engine error must not turn into a computed match score (0). Issue: D51. */
    @Test
    void engineErrorIsNeverTreatedAsAComputedMatchScore() {
        stubFor(post(urlEqualTo("/api/v1/match")).willReturn(aResponse().withStatus(503)));
        MatchRequest m = new MatchRequest();
        m.studentSkills = List.of("Java");
        m.requiredSkills = List.of("Java");
        m.niceToHaveSkills = List.of();
        try {
            MatchResult result = client.match(m);
            fail("REL-01: the Engine answered 503 but the Portal returned a match score of " + result.score());
        } catch (EngineUnavailableException expected) {
            // refusing the operation is the specified behaviour
        }
    }
}

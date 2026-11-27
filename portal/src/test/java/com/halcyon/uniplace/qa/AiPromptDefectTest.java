package com.halcyon.uniplace.qa;

import com.halcyon.uniplace.ai.AiRequestContext;
import com.halcyon.uniplace.ai.PromptBuilder;
import com.halcyon.uniplace.domain.Company;
import com.halcyon.uniplace.domain.CompanyStatus;
import com.halcyon.uniplace.domain.Posting;
import com.halcyon.uniplace.domain.Student;
import com.halcyon.uniplace.support.IntegrationTest;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * White-box tests on the request the Portal really sends to the AI provider: they call the shipped
 * {@link PromptBuilder} (not a copy of it). A FAILING test is the evidence for the issue in its Javadoc.
 */
class AiPromptDefectTest extends IntegrationTest {

    private Student student;
    private String prompt;

    @BeforeEach
    void buildPrompt() {
        Company c = company("QTech", CompanyStatus.APPROVED);
        Posting p = openPosting(c, "Backend Intern", List.of("Java", "SQL"), 1);
        student = student("3.40", List.of("Java"));
        prompt = new PromptBuilder()
                .feedbackPrompt(new AiRequestContext(student, p, "I used Java and SQL in two course projects."))
                .get(0).content();
    }

    /** AI-03: the request carries only the posting and the letter, never name, student number or GPA. Issue: D08. */
    @Test
    void promptCarriesNoPersonalData() {
        assertFalse(prompt.contains(student.getFullName()), "AI-03: the student's name is sent to the provider");
        assertFalse(prompt.contains(student.getStudentNumber()), "AI-03: the student number is sent to the provider");
        assertFalse(prompt.contains("GPA"), "AI-03: the student's GPA is sent to the provider");
    }

    /** AI-10: internal settings such as the shortlist threshold are never disclosed to the provider. Issue: D32. */
    @Test
    void promptDoesNotDiscloseTheShortlistThreshold() {
        assertFalse(prompt.toLowerCase().contains("reject applications that score below"),
                "AI-10: the prompt tells the provider the internal shortlist threshold");
    }

    /** AI-11: the worked example in the prompt is itself a valid answer (integer score 0-100). Issue: D42. */
    @Test
    void workedExampleHasAnIntegerScore() {
        Matcher m = Pattern.compile("Example of a valid answer:\\s*\\{\"score\":\\s*([0-9.]+)").matcher(prompt);
        assertTrue(m.find(), "the prompt should contain a worked example");
        assertTrue(m.group(1).matches("\\d{1,3}"),
                "AI-11: the example's score must be an integer 0-100, but it is " + m.group(1));
    }
}

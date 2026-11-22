package com.halcyon.uniplace.qa;

import com.halcyon.uniplace.domain.Application;
import com.halcyon.uniplace.domain.ApplicationState;
import com.halcyon.uniplace.domain.Company;
import com.halcyon.uniplace.domain.CompanyStatus;
import com.halcyon.uniplace.domain.Posting;
import com.halcyon.uniplace.domain.Role;
import com.halcyon.uniplace.domain.Student;
import com.halcyon.uniplace.domain.User;
import com.halcyon.uniplace.support.IntegrationTest;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * Server-side access-control and CSRF reproduction tests (USR-05, SEC-02, SEC-05).
 * A FAILING test here is the evidence for the defect named in its Javadoc.
 */
@AutoConfigureMockMvc
class SecurityAccessTest extends IntegrationTest {

    @Autowired MockMvc mvc;

    private User namedStudent(String username, String gpa) {
        Student s = student(gpa, List.of("Java"));
        User u = new User(username, "{noop}unused", Role.STUDENT, s.getFullName(), s.getEmail());
        u.setStudent(s);
        return users.save(u);
    }

    /** USR-05 / SEC-05: a student may open only their own application. Issue: D05. */
    @Test
    void studentCannotOpenAnotherStudentsApplication() throws Exception {
        Company c = company("QTech", CompanyStatus.APPROVED);
        Posting p = openPosting(c, "Backend Intern", List.of("Java"), 1);
        User owner = namedStudent("owner", "3.00");
        Application a = application(owner.getStudent(), p, ApplicationState.SUBMITTED, 70);
        namedStudent("intruder", "3.00");

        mvc.perform(get("/applications/" + a.getId()).with(user("intruder").roles("STUDENT")))
                .andExpect(status().isForbidden());
    }

    /** SEC-02: every form that changes data is protected against CSRF, including Settings. Issue: D31. */
    @Test
    void settingsPostWithoutCsrfTokenIsRejected() throws Exception {
        users.save(new User("coord", "{noop}unused", Role.COORDINATOR, "Coord", "coord@uniplace.local"));
        // No .with(csrf()): a CSRF-protected endpoint must reject this with 403.
        mvc.perform(post("/coordinator/settings").param("shortlist.threshold", "60")
                        .with(user("coord").roles("COORDINATOR")))
                .andExpect(status().isForbidden());
    }
}
